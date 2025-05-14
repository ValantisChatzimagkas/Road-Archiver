from datetime import datetime, UTC
import json
from typing import Dict, Optional

from fastapi import UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from shapely.geometry.geo import mapping
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.db.models import RoadEdge, User, RoadNetwork, UserRolesOptions
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape


# HELPERS
async def normalize_lanes(value):
    """Normalize lanes value to a string."""
    if isinstance(value, list):
        return ",".join(map(str, value))
    elif value is not None:
        return str(value)
    return None


async def normalize_width(value):
    """Normalize width value to a list of floats."""
    if isinstance(value, list):
        try:
            return [float(w) for w in value]
        except (ValueError, TypeError):
            return None
    elif value is not None:
        try:
            return [float(value)]
        except (ValueError, TypeError):
            return None
    return None


async def create_road_edge(feature: Dict, network_id: int, current_user_id: int) -> RoadEdge:
    geometry = from_shape(shape(feature.get("geometry")), srid=4326)
    properties = feature.get("properties", {})

    lanes_value = await normalize_lanes(properties.get("lanes"))
    width_value = await normalize_width(properties.get("width"))
    known_fields = {"name", "ref", "oneway", "length", "tunnel", "lanes", "width"}

    return RoadEdge(
        geometry=geometry,
        name=properties.get("name"),
        ref=properties.get("ref"),
        lanes=lanes_value,
        oneway=properties.get("oneway"),
        length=properties.get("length"),
        width=width_value,
        tunnel=properties.get("tunnel"),
        extra_properties={k: v for k, v in properties.items() if k not in known_fields},
        is_current=True,
        network_id=network_id,
        user_id=current_user_id
    )


async def mark_edges_as_not_current(db, network_id):
    """Mark all current edges in the network as not current."""
    db.query(RoadEdge).filter(
        and_(RoadEdge.network_id == network_id, RoadEdge.is_current == True)
    ).update({"is_current": False})


async def build_updated_edge(feature, network_id, current_user_id):
    """Build a new edge from a GeoJSON feature."""
    geom = shape(feature["geometry"])
    geom_pg = from_shape(geom, srid=4326)

    properties = feature.get("properties", {})

    lanes_value = await normalize_lanes(properties.get("lanes"))
    width_value = await normalize_width(properties.get("width"))

    fields = {"name", "ref", "oneway", "length", "tunnel"}

    edge = RoadEdge(
        geometry=geom_pg,
        name=properties.get("name"),
        ref=properties.get("ref"),
        lanes=lanes_value,
        oneway=properties.get("oneway"),
        length=properties.get("length"),
        width=width_value,
        tunnel=properties.get("tunnel"),
        extra_properties={
            k: v for k, v in properties.items()
            if k not in fields.union({"lanes", "width"})
        },
        is_current=True,
        timestamp=datetime.now(UTC),
        network_id=network_id,
        user_id=current_user_id
    )
    return edge


# ENDPOINT HANDLERS
async def upload_road_network(db: Session, current_user: User, file: UploadFile = File(...)):
    try:
        content = file.file.read()
        geojson_data = json.loads(content)

        network_name = geojson_data.get("name") or "Unnamed Network"
        timestamp = geojson_data.get("timestamp", datetime.now(UTC))

        network = RoadNetwork(
            name=network_name,
            timestamp=timestamp,
            user_id=current_user.id
        )
        db.add(network)
        db.flush()

        features = geojson_data.get("features", [])

        edges_to_add = [
            await create_road_edge(feature, network.id, current_user.id)
            for feature in features
        ]

        db.bulk_save_objects(edges_to_add)
        db.commit()

        return {"message": "Upload successful", "network_id": network.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Upload failed: {str(e)}"
        )


async def get_network(db: Session,
                      current_user: User,
                      network_id: int,
                      timestamp: Optional[datetime] = None
                      ):
    try:

        if current_user.role == UserRolesOptions.ADMIN:
            network = db.query(RoadNetwork).filter_by(id=network_id).first()
        else:
            network = db.query(RoadNetwork).filter_by(
                id=network_id,
                user_id=current_user.id
            ).first()

        if network is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Network not found")

        query = db.query(RoadEdge).filter(RoadEdge.network_id == network_id)

        if timestamp:
            query = query.filter(RoadEdge.timestamp <= timestamp)
        else:
            query = query.filter(RoadEdge.is_current == True)

        edges = query.all()

        if not edges:
            return JSONResponse(content={"type": "FeatureCollection", "features": []})

        features = [
            {
                "type": "Feature",
                "geometry": mapping(to_shape(edge.geometry)),
                "properties": {
                    "id": edge.id,
                    "timestamp": edge.timestamp.isoformat(),
                    "is_current": edge.is_current
                }
            }
            for edge in edges
        ]

        return JSONResponse(content={"type": "FeatureCollection", "features": features})

    except SQLAlchemyError as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred"
        )


async def update_network_from_file(db: Session,
                                   current_user: User,
                                   network_id: int,
                                   file: UploadFile = File(...)
                                   ):
    try:
        current_user_id = current_user.id

        if current_user.role == UserRolesOptions.ADMIN:
            network = db.query(RoadNetwork).filter_by(id=network_id).first()
        else:
            network = db.query(RoadNetwork).filter_by(
                id=network_id,
                user_id=current_user_id
            ).first()

        if network is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Network not found")

        content = await file.read()
        geojson_data = json.loads(content)
        current_user_id = current_user_id

        features = geojson_data.get("features", [])

        if features:
            await mark_edges_as_not_current(db, network_id)

        new_features = [await build_updated_edge(feature, network_id, current_user_id) for feature in features]
        db.bulk_save_objects(new_features)
        db.commit()
        return {"message": "Network updated successfully", "network_id": network.id}


    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Update failed: {str(e)}")

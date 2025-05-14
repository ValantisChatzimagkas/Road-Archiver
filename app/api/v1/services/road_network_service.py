from datetime import datetime, UTC
import json
from typing import Dict

from fastapi import UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.db.models import RoadEdge, User, RoadNetwork
from geoalchemy2.shape import from_shape
from shapely.geometry import shape


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

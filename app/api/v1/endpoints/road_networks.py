from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.db.models import RoadEdge, User, RoadNetwork
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape

import json
# from app.schemas import CreateRoadNetwork


router = APIRouter(prefix="/networks", tags=["Networks"])


def parse_width(value):
    """Normalize 'width' input into float or list of floats"""
    if value is None:
        return None
    if isinstance(value, list):
        try:
            return [float(v) for v in value]
        except ValueError:
            raise ValueError(f"Invalid width list: {value}")
    try:
        return [float(value)]
    except ValueError:
        raise ValueError(f"Invalid width value: {value}")

@router.post("/networks/upload")
async def upload_road_network(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        content = await file.read()
        geojson_data = json.loads(content)

        network_name = geojson_data.get("name") or "Unnamed Network"
        timestamp = geojson_data.get("timestamp")


        network = RoadNetwork(
            name=network_name,
            timestamp=timestamp,
        )
        db.add(network)
        db.commit()
        db.refresh(network)

        return {"message": "Upload successful", "network_id": network.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Upload failed: {str(e)}")
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.services.authentication_service import get_current_user
from app.core.database import get_db
from app.api.v1.services import road_network_service
from app.db.models import User

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
        current_user: User = Depends(get_current_user)
):
    await road_network_service.upload_road_network(db=db, file=file, current_user=current_user)
    return {"message": "File Uploaded"}


@router.get("/networks/{network_id}/edges")
async def get_network(network_id: int,
                      timestamp: Optional[datetime] = None,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)
                      ):
    network = await road_network_service.get_network(
        db=db, current_user=current_user, network_id=network_id, timestamp=timestamp
    )
    return network

@router.post("/networks/{network_id}/update")
async def update_network_from_file(network_id: int,
                                   db: Session = Depends(get_db),
                                   current_user: User = Depends(get_current_user),
                                   file: UploadFile = File(...)
                                   ):
    result = await road_network_service.update_network_from_file(db=db,
                                                                 current_user=current_user,
                                                                 network_id=network_id, file=file)
    return result
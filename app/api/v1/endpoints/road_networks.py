from datetime import datetime

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.v1.services import road_network_service
from app.api.v1.services.authentication_service import get_current_user
from app.core.database import get_db
from app.db.models import User
from app.schemas import NetworkUpdateResponse

router = APIRouter(prefix="/networks", tags=["Networks"])


@router.post(
    "/upload",
    summary="Upload a new road network file",
    description="""
             Uploads a road network file, in geojson format.

             - Requires authentication.
             - The file must be valid and properly formatted.
             """,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {"description": "File uploaded successfully"},
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid file format or upload error"
        },
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    },
)
async def upload_road_network(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    await road_network_service.upload_road_network(
        db=db, file=file, current_user=current_user
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content={"message": "File Uploaded"}
    )


@router.get(
    "/{network_id}/edges",
    summary="Retrieve road network edges",
    description="""
            Returns the edges of a specific road network by ID.

            - Optionally filter by timestamp (to get the network state at a given time).
            - Requires authentication.
            """,
    responses={
        status.HTTP_200_OK: {"description": "Edges retrieved successfully"},
        status.HTTP_404_NOT_FOUND: {"description": "Road network not found"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    },
)
async def get_network(
    network_id: int,
    timestamp: datetime | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JSONResponse:
    network = await road_network_service.get_network(
        db=db, current_user=current_user, network_id=network_id, timestamp=timestamp
    )
    return JSONResponse(status_code=status.HTTP_200_OK, content=network)


@router.post(
    "/{network_id}/update",
    summary="Update a road network from a file",
    description="""
             Updates the given road network using a new uploaded file.

             - Requires authentication.
             - The file content must be valid.
             """,
    responses={
        status.HTTP_200_OK: {"description": "Network updated successfully"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid file or update failed"},
        status.HTTP_404_NOT_FOUND: {"description": "Road network not found"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
    },
)
async def update_network_from_file(
    network_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
) -> NetworkUpdateResponse:
    result = await road_network_service.update_network_from_file(
        db=db, current_user=current_user, network_id=network_id, file=file
    )
    return NetworkUpdateResponse(message=result.message, network_id=result.network_id)

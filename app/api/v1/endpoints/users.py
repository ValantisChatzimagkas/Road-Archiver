from typing import List

from fastapi import APIRouter, Depends, Body, Response, status
from sqlalchemy.orm import Session
from app.api.v1.services import users_service
from app.api.v1.services.authentication_service import get_current_user
from app.core.database import get_db
from app.db.models import User, UserRolesOptions
from app.schemas import CreateUser, ReadUser, ReadRoadNetwork

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=ReadUser,
    summary="Create a new user",
    description="Creates a user with the provided details.",
    responses={status.HTTP_201_CREATED: {"description": "User successfully created"}},
)
async def create_user(
    request: CreateUser = Body(
        ...,
        example=dict(
            username="my_user",
            email="my_user@coldmail.com",
            hashed_password="A_sword",
            role=UserRolesOptions.USER,
        ),
    ),
    db: Session = Depends(get_db),
):
    created_user = await users_service.create_user(request=request, db=db)
    return created_user


@router.get(
    "/{id}",
    response_model=ReadUser,
    summary="Get user by id",
    description="""
             This endpoint has 2 modes.
             <br>
             <ul>
                <li> if user is **Admin** then that user can get every user. </li>
                <li> if user is **User** then this user can retrieve only itself.</li>
             </ul>
             
             - Requires authentication.
             """,
    responses={
        status.HTTP_200_OK: {"description": "Found User"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Not Allowed"},
    },
)
async def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = await users_service.get_user_by_id(
        user_id=id, db=db, current_user=current_user
    )
    return user


@router.get(
    "/{id}/networks",
    response_model=List[ReadRoadNetwork],
    summary="Get road networks for user",
    description="""
             This endpoint will retrieve all the road networks that are associated to a user.

             - Requires authentication.
             """,
    responses={
        status.HTTP_200_OK: {"description": "Found Networks"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Not Allowed"},
    },
)
async def get_road_networks_for_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    networks = await users_service.get_road_networks_for_user(
        user_id=id, db=db, current_user=current_user
    )
    return networks


@router.delete(
    "/{id}",
    summary="Deletes a user",
    description="""
               Delete a user, in order to user this endpoint, the caller must be an Admin.
               
               - Requires authentication.
               """,
    responses={
        status.HTTP_200_OK: {"description": "User was deleted"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Not Allowed"},
    },
)
async def delete_user_endpoint(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await users_service.delete_user(
        db=db, user_id=id, current_user=current_user
    )
    return result

from typing import Annotated

from fastapi import APIRouter, Body, status

from app.api.v1.services import users_service
from app.api.v1.services.authentication_service import CurrentUser
from app.core.database import DbSession
from app.db.models import User, UserRolesOptions
from app.schemas import CreateUser, MessageResponse, ReadRoadNetwork, ReadUser

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/",
    response_model=ReadUser,
    summary="Create a new user",
    description="Creates a user with the provided details.",
    responses={status.HTTP_201_CREATED: {"description": "User successfully created"}},
)
def create_user(
    request: Annotated[
        CreateUser,
        Body(
            example=dict(
                username="my_user",
                email="my_user@coldmail.com",
                hashed_password="A_sword",
                role=UserRolesOptions.USER,
            ),
        ),
    ],
    db: DbSession,
) -> User:
    created_user = users_service.create_user(request=request, db=db)
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
def get_user(
    id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> User:
    user = users_service.get_user_by_id(user_id=id, db=db, current_user=current_user)
    return user


@router.get(
    "/{id}/networks",
    response_model=list[ReadRoadNetwork],
    summary="Get road networks for user",
    description="""
             This endpoint will retrieve all the road networks associated with a user.

             - Requires authentication.
             """,
    responses={
        status.HTTP_200_OK: {"description": "Found Networks"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Not Allowed"},
    },
)
def get_road_networks_for_user(
    id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> list[ReadRoadNetwork]:
    networks = users_service.get_road_networks_for_user(
        user_id=id, db=db, current_user=current_user
    )
    return networks


@router.delete(
    "/{id}",
    summary="Deletes a user",
    description="""
               Delete a user. The caller must be an Admin.
               
               - Requires authentication.
               """,
    responses={
        status.HTTP_200_OK: {"description": "User was deleted"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Not Allowed"},
    },
)
def delete_user_endpoint(
    id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> MessageResponse:
    result = users_service.delete_user(db=db, user_id=id, current_user=current_user)
    return MessageResponse(**result)

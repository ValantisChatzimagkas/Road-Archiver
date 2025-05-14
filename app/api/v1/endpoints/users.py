from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.v1.services import users_service
from app.api.v1.services.authentication_service import get_current_user
from app.core.database import get_db
from app.db.models import User
from app.schemas import CreateUser, ReadUser

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=ReadUser)
async def create_user(request: CreateUser, db: Session = Depends(get_db)):
    created_user = await users_service.create_user(request=request, db=db)
    return created_user


@router.get("/{id}", response_model=ReadUser)
async def get_user(id: int, db: Session = Depends(get_db)):
    user = await users_service.get_user_by_id(user_id=id, db=db)
    return user


@router.delete("/{id}")
async def delete_user(id:int, db: Session = Depends(get_db)):
    result = await users_service.delete_user(db=db, user_id=id)
    return result

from fastapi import HTTPException, status
from httpx import request
from pydantic import EmailStr
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import Hasher
from app.db.models import User, UserRolesOptions
from app.schemas import CreateUser


async def create_user(db: Session, request: CreateUser):
    try:
        new_user = User(
            username=request.username,
            email=request.email,
            hashed_password= Hasher.hash_password(request.hashed_password),
            role=request.role
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Failed to create user, {e}")


async def get_user_by_id(db: Session, user_id: int, current_user: User):
    try:
        user = db.query(User).filter_by(id=user_id).first()

        if current_user.role != UserRolesOptions.ADMIN.value and current_user.id != user.id:
            raise HTTPException(detail="Action not permitted", status_code=status.HTTP_401_UNAUTHORIZED)


        if not user:
            raise HTTPException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)

        return user

    except SQLAlchemyError:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred"
        )


async def delete_user(db: Session, user_id: int):
    try:

        user = db.query(User).filter_by(id=user_id).first()

        if user.role != UserRolesOptions.ADMIN:
            raise HTTPException(detail="Action not permitted", status_code=status.HTTP_401_UNAUTHORIZED)

        if not user:
            raise HTTPException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)

        db.delete(user)
        db.commit()
        return {"detail": "User deleted successfully"}

    except SQLAlchemyError:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred"
        )


# for now, I use this for authenticating users, does not get used by a respective endpoint
async def get_user_by_email(db: Session, email: EmailStr):
    try:
        user =  db.query(User).filter_by(email=email).first()

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    except SQLAlchemyError as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred"
        )

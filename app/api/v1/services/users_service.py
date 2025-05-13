from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from app.db.models import User
from app.schemas import CreateUser


async def create_user(db: Session, request: CreateUser):
    try:
        new_user = User(
            username=request.username,
            email=request.email,
            hashed_password=request.hashed_password
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Failed to create user, {e}")


async def get_user_by_id(db: Session, user_id: int):
    try:
        user = db.query(User).filter_by(id=user_id).first()

        if not user:
            raise HTTPException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)

        return user

    except SQLAlchemyError:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred"
        )


# for now, I use this for authenticating users, does not get used by a respective endpoint
async def get_user_by_email(db: Session, user_email: EmailStr):
    try:
        user = db.query(User).filter_by(email=user_email)

        if not user:
            raise HTTPException(detail="User not found", status_code=status.HTTP_404_NOT_FOUND)

    except SQLAlchemyError as e:

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal error occurred"
        )

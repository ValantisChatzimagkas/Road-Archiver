from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated
from app.core.database import get_db
from app.schemas import Token
from app.api.v1.services.authentication_service import authenticate_user, create_access_token

router = APIRouter(prefix="/auth", tags=["authentication"])

ACCESS_TOKEN_EXPIRATION_TIME = 1440  # minutes


@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                db: Session = Depends(get_db)
                ) -> Token:
    user = await authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token_expiration = timedelta(minutes=ACCESS_TOKEN_EXPIRATION_TIME)
    access_token = await create_access_token(
        data={"sub": user.email}, expiration_delta=access_token_expiration
    )
    return Token(access_token=access_token, token_type="bearer")

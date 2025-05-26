from datetime import UTC, datetime, timedelta
from typing import Annotated, Union, Any, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from app.api.v1.services.users_service import get_user_by_email
from app.core.config import settings
from app.core.database import get_db
from app.core.security import Hasher
from app.db.models import User
from app.schemas import TokenData

SECRET_KEY = settings.jwt_secret_key
ALGORITHM = "HS256"
EXPIRATION_THRESHOLD = 30  # minutes

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def authenticate_user(
    email: str, password: str, db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Authenticates a user using their email and password.
    Returns the User if valid, otherwise None.
    """
    user = await get_user_by_email(db, email)
    if not user or not Hasher.verify_password(password, user.hashed_password):
        return None
    return user


async def create_access_token(
    data: dict[str, Any], expiration_delta: timedelta | None = None
) -> str:
    """
    Generates JWT access token
    :param data:
    :param expiration_delta:
    :return:
    """
    to_encode = data.copy()

    if expiration_delta:
        expire = datetime.now(UTC) + expiration_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=EXPIRATION_THRESHOLD)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
) -> User:
    """
    Implements logic for getting current user
    :param token:
    :param db:
    :return:
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Failed to validate the provided credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)

    except InvalidTokenError:
        raise credentials_exception

    user = await get_user_by_email(db, email=token_data.email)

    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user

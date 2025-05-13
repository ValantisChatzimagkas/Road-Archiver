from enum import Enum
from sqlalchemy import Column, String, Integer
from sqlalchemy import Enum as SqlEnum

from app.core.database import Base


class UserRolesOptions(str, Enum):
    """
    ADMIN: 	Full control: manage users, system settings, content, etc
    MODERATOR: Limited admin: review/manage content or users (but not system settings)
    USER: Regular authenticated user
    GUEST: Unauthenticated or very limited account
    """
    ADMIN = "ADMIN"
    MODERATOR = "MODERATOR"
    USER = "USER"
    GUEST = "GUEST"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SqlEnum(UserRolesOptions), default=UserRolesOptions.USER, nullable=False)

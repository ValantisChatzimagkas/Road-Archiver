from datetime import datetime, UTC
from enum import Enum
from typing import List, Dict, Any, Optional

from geoalchemy2 import Geometry
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Float
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    role: Mapped[UserRolesOptions] = mapped_column(SqlEnum(UserRolesOptions), default=UserRolesOptions.USER, nullable=False)

    networks: Mapped[List["RoadNetwork"]] = relationship("RoadNetwork", back_populates="user")
    edges: Mapped[List["RoadEdge"]] = relationship("RoadEdge", back_populates="user")


class RoadNetwork(Base):
    __tablename__ = "road_networks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC), nullable=False)
    user_id: Mapped[[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="networks")
    edges: Mapped["RoadEdge"] = relationship("RoadEdge", back_populates="network", cascade="all, delete-orphan")


class RoadEdge(Base):
    __tablename__ = "road_edges"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    ref: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    lanes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    oneway: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    length: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    width: Mapped[Optional[List[float]]] = mapped_column(ARRAY(Float), nullable=True)
    tunnel: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    extra_properties: Mapped[Dict[str, Any]] = mapped_column(JSONB, default={})
    geometry: Mapped[Dict[str, Any]] = mapped_column(Geometry(geometry_type='GEOMETRY', srid=4326), nullable=False)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC), nullable=False)
    network_id: Mapped[int] = mapped_column(Integer, ForeignKey("road_networks.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)

    network: Mapped["RoadNetwork"] = relationship("RoadNetwork", back_populates="edges")
    user: Mapped["User"] = relationship("User", back_populates="edges")

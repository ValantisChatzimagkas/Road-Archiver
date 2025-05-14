from datetime import datetime, UTC
from enum import Enum
from geoalchemy2 import Geometry
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Float
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship

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

    networks = relationship("RoadNetwork", back_populates="user")
    edges = relationship("RoadEdge", back_populates="user")



class RoadNetwork(Base):
    __tablename__ = "road_networks"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=datetime.now(UTC), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="networks")
    edges = relationship("RoadEdge", back_populates="network", cascade="all, delete-orphan")


class RoadEdge(Base):
    __tablename__ = "road_edges"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=True)
    ref = Column(String, nullable=True)
    lanes = Column(String, nullable=True)
    oneway = Column(Boolean, nullable=True)
    length = Column(Float, nullable=True)
    width = Column(ARRAY(Float), nullable=True)
    tunnel = Column(String, nullable=True)
    extra_properties = Column(JSONB, default={})
    geometry = Column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=False)
    is_current = Column(Boolean, default=True)  # track historical versions
    timestamp = Column(DateTime(timezone=True), default=datetime.now(UTC), nullable=False)  # Added timestamp field
    network_id = Column(Integer, ForeignKey("road_networks.id"), nullable=False)

    network = relationship("RoadNetwork", back_populates="edges")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="edges")
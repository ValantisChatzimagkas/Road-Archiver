from typing import Dict

from pydantic import BaseModel, EmailStr

from app.db.models import UserRolesOptions


# -------------------- User Schemas --------------------
class CreateUser(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str
    role: UserRolesOptions


class ReadUser(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRolesOptions

    class Config:
        orm_mode = True


# --------------- Authentication Schemas ---------------
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: EmailStr | None = None


class UserAuth(BaseModel):
    id: int
    username: str
    email: EmailStr


# --------- RoadNetworks --------
class ReadRoadNetwork(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class NetworkUpdateResponse(BaseModel):
    message: str
    network_id: int


class UploadRoadNetworkResponse(BaseModel):
    message: str
    network_id: int


class UpdateRoadNetworkResponse(BaseModel):
    message: str
    network_id: int


# -------------- Common ----------------------
class MessageResponse(BaseModel):
    detail: str

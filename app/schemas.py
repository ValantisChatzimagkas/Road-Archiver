from pydantic import BaseModel, EmailStr, Field

from app.db.models import UserRolesOptions


# -------------------- User Schemas --------------------
class CreateUser(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str



class ReadUser(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRolesOptions

    class Config:
        orm_mode = True
from pydantic import BaseModel, EmailStr, Field


# -------------------- User Schemas --------------------
class CreateUser(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str


class ReadUser(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True
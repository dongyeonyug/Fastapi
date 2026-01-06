from datetime import datetime
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    email: str
    username: str


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

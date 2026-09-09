from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, EmailStr

Role = Literal["admin", "user", "editor"]


class UserBase(BaseModel):
    email: str
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class UserPublic(UserBase):
    id: int
    role: Role
    is_active: bool


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    full_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class RoleUpdate(BaseModel):
    role: Role


class TokenData(BaseModel):
    subject: str
    username: str

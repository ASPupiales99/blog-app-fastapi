from pydantic import BaseModel, ConfigDict


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    subject: str
    username: str


class UserPublic(BaseModel):
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)

from datetime import datetime, timezone, timedelta
from typing import Optional, Literal

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import ExpiredSignatureError, InvalidTokenError, PyJWTError
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.auth.repository import get_user_repository
from app.core.config import Settings
from app.core.db import get_db
from app.model import User

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"}
)


def raise_expire_token():
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired",
                         headers={"WWW-Authenticate": "Bearer"})


def raise_forbidden():
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden", )


def invalid_credentials():
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


def create_access_token(subject: str, minutes: int | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes or Settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": subject, "exp": expire}, Settings.JWT_SECRET, algorithm=Settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    payload = jwt.decode(token, key=Settings.JWT_SECRET, algorithms=[Settings.JWT_ALGORITHM])
    return payload


async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = decode_token(token)
        subject: Optional[str] = payload.get("sub")
        if not subject:
            raise credentials_exception

        user_id = int(subject)
    except ExpiredSignatureError:
        raise raise_expire_token()
    except InvalidTokenError:
        raise credentials_exception
    except PyJWTError:
        raise invalid_credentials

    user = db.get(User, user_id)

    if not user or not user.is_active:
        raise invalid_credentials

    return user


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def require_role(min_role: Literal["user", "editor", "admin"]):
    order = {"user": 0, "editor": 1, "admin": 2}

    def evaluation(user: User = Depends(get_current_user)) -> User:
        if order[user.role] < order[min_role]:
            raise raise_forbidden()
        return user

    return evaluation


async def auth2_token(form: OAuth2PasswordRequestForm = Depends(), repository=Depends(get_user_repository)):
    user = repository.get_user_by_email(form.username)

    if not user or not verify_password(form.password, user.password):
        raise invalid_credentials()

    token = create_access_token(subject=str(user.id))

    return {"access_token": token, "token_type": "bearer"}


require_user = require_role("user")
require_editor = require_role("editor")
require_admin = require_role("admin")

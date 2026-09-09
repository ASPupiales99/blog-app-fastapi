from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.exc import SQLAlchemyError

from app.auth.repository import get_user_repository
from app.auth.schemas import UserPublic, UserCreate, TokenResponse, UserLogin, RoleUpdate
from app.core.security import get_current_user, hash_password, verify_password, create_access_token, require_admin, \
    auth2_token
from app.model import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, repository=Depends(get_user_repository)):
    if repository.get_user_by_email(payload.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        user = repository.create_user(
            email=payload.email,
            password=hash_password(payload.password),
            full_name=payload.full_name
        )

        repository.db.commit()
        repository.db.refresh(user)

        return UserPublic.model_validate(user)
    except SQLAlchemyError:
        repository.db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error registering user")


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLogin, repository=Depends(get_user_repository)):
    user = repository.get_user_by_email(payload.email)

    if not user or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=str(user.id))

    return TokenResponse(access_token=token, user=UserPublic.model_validate(user))


@router.get("/me", response_model=UserPublic)
async def read_me(current: User = Depends(get_current_user)):
    return UserPublic.model_validate(current)


@router.put("/role/{user_id}", response_model=UserPublic)
def update_role(
        user_id: int = Path(..., ge=1),
        payload: RoleUpdate = None,
        repository=Depends(get_user_repository),
        _admin: User = Depends(require_admin)
):
    user = repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updated = repository.set_role(user, payload.role)

    repository.db.commit()
    repository.db.refresh(updated)

    return UserPublic.model_validate(updated)


@router.post("/token")
async def token_endpoint(response=Depends(auth2_token)):
    return response

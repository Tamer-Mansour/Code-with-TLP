from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import (
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest, TokenPair
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


def _authenticate(db: Session, identifier: str, password: str) -> User | None:
    user = db.query(User).filter(or_(User.email == identifier, User.username == identifier)).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
    return user


def _tokens_for(user: User) -> TokenPair:
    return TokenPair(
        access_token=create_access_token(user.id, extra={"role": user.role.value}),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> User:
    existing = (
        db.query(User)
        .filter(or_(User.email == payload.email, User.username == payload.username))
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Email or username already taken")

    user = User(
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=UserRole.student,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenPair:
    user = _authenticate(db, payload.identifier, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return _tokens_for(user)


@router.post("/login/oauth", response_model=TokenPair, include_in_schema=False)
def login_oauth(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> TokenPair:
    """OAuth2 password flow endpoint for Swagger 'Authorize' button."""
    user = _authenticate(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return _tokens_for(user)


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenPair:
    try:
        data = decode_token(payload.refresh_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if data.get("type") != REFRESH_TOKEN_TYPE:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = db.get(User, int(data.get("sub", 0)))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return _tokens_for(user)


@router.get("/me", response_model=UserRead)
def me(current: User = Depends(get_current_user)) -> User:
    return current

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import User
from ..schemas import DevLoginIn, GoogleLoginIn, RuntimeConfigOut, TokenOut, UserOut
from ..security import create_access_token, get_current_user, verify_google_credential
from ..services.providers import ProviderChain


router = APIRouter(tags=["authentication"])


def upsert_user(db: Session, email: str, display_name: str, subject: str | None = None) -> User:
    normalized_email = email.strip().lower()
    user = db.scalar(select(User).where(User.email == normalized_email))
    role = "admin" if normalized_email in settings.admin_email_set else "member"
    if user is None:
        user = User(
            email=normalized_email,
            display_name=display_name.strip() or normalized_email.split("@", 1)[0],
            provider_subject=subject,
            role=role,
        )
        db.add(user)
    else:
        user.display_name = display_name.strip() or user.display_name
        user.provider_subject = subject or user.provider_subject
        user.role = role
    db.flush()
    return user


@router.get("/config", response_model=RuntimeConfigOut)
def runtime_config():
    return RuntimeConfigOut(
        auth_mode=settings.auth_mode,
        google_client_id=settings.google_client_id,
        providers=ProviderChain().names,
        features=["citations", "history", "bookmarks", "feedback", "document-upload", "daily-wisdom"],
    )


@router.post("/auth/dev", response_model=TokenOut)
def development_login(payload: DevLoginIn, db: Session = Depends(get_db)):
    if settings.auth_mode != "development":
        raise HTTPException(status_code=404, detail="Development login is disabled")
    user = upsert_user(db, payload.email, payload.display_name)
    return TokenOut(access_token=create_access_token(user), user=UserOut.model_validate(user))


@router.post("/auth/google", response_model=TokenOut)
def google_login(payload: GoogleLoginIn, db: Session = Depends(get_db)):
    claims = verify_google_credential(payload.credential)
    user = upsert_user(
        db,
        email=claims["email"],
        display_name=claims.get("name") or claims["email"].split("@", 1)[0],
        subject=claims["sub"],
    )
    return TokenOut(access_token=create_access_token(user), user=UserOut.model_validate(user))


@router.get("/auth/me", response_model=UserOut)
def current_user(user: User = Depends(get_current_user)):
    return user

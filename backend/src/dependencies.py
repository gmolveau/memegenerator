"""Reusable FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.requests import Request

from src.database import get_db
from src.models import User
from src.storage import get_disk
from src.storage.disk import StorageDisk

SessionDep = Annotated[Session, Depends(get_db)]

DiskDep = Annotated[StorageDisk, Depends(get_disk)]

ADMIN_ROLES = {"admin", "superadmin"}


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    """Return the logged-in User ORM object, or None if not authenticated."""
    session_user = request.session.get("user")
    if not session_user:
        return None
    sub = session_user.get("sub")
    if not sub:
        return None
    return db.query(User).filter(User.sub == sub).first()


CurrentUserDep = Annotated[User | None, Depends(get_current_user)]


def require_admin(request: Request) -> None:
    """Raise 401 if not logged in, 403 if not an admin."""
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if user.get("role") not in ADMIN_ROLES:
        raise HTTPException(status_code=403, detail="Admin role required")


AdminDep = Depends(require_admin)

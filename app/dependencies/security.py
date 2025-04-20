from fastapi import Header, HTTPException

from app.core.config import ADMIN_KEY


def require_admin(admin_key: str = Header(None)):
    if admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Not authorized")

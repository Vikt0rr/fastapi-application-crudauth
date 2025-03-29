from fastapi import Depends, HTTPException, status
from app import schemas
from app.auth import get_current_user


async def get_current_admin(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
    return current_user


async def verify_admin_access(current_user: schemas.User = Depends(get_current_admin)):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive admin account"
        )
    return current_user

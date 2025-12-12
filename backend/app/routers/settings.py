from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.models.user import User

router = APIRouter()

@router.patch("/settings", response_model=Dict[str, Any])
@router.patch("/settings", response_model=Dict[str, Any])
async def update_settings(
    settings: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Update user settings (e.g. auto_approve, theme, etc.)
    Merges with existing settings.
    """
    current_settings = current_user.settings or {}
    
    if isinstance(current_settings, str):
        # Handle case where JSON might be stored as string (shouldn't happen with JSON type but safe check)
        import json
        try:
            current_settings = json.loads(current_settings)
        except:
            current_settings = {}
            
    # Merge updates
    current_settings.update(settings)
    
    current_user.settings = current_settings
    # Force SQLAlchemy to detect change on mutable JSON/Dict
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(current_user, "settings")
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user.settings

@router.get("/settings", response_model=Dict[str, Any])
@router.get("/settings", response_model=Dict[str, Any])
async def get_settings(
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Get user settings.
    """
    return current_user.settings or {}

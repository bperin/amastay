from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any, Callable
from functools import wraps
import os
import jwt
from jwt import PyJWTError
from auth_utils import require_admin_and_owner, require_admin_or_owner


def require_role(*allowed_roles: str):
    """Create a dependency that checks if the user has one of the allowed roles"""

    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_type = current_user.get("user_type")
        if not user_type or user_type not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Access denied. Required roles: {', '.join(allowed_roles)}")
        return current_user

    return role_checker


# Convenience dependencies for common role checks
require_owner = require_role("owner")
require_manager = require_role("manager")
require_owner_or_manager = require_role("owner", "manager")


@router.post("/sensitive-operation")
async def sensitive_operation(data: SomeInput, current_user: dict = Depends(require_admin_and_owner)):
    """Only users who are both admins and owners can perform this operation"""
    # ... implementation ...


@router.get("/less-sensitive-operation")
async def less_sensitive_operation(current_user: dict = Depends(require_admin_or_owner)):
    """Users who are either admins OR owners can perform this operation"""
    # ... implementation ...

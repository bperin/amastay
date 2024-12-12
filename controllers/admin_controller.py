from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any, Callable
from functools import wraps
import os
import jwt
from jwt import PyJWTError
from auth_utils import get_current_user, require_admin_and_owner, require_admin_or_owner


@router.post("/sensitive-operation")
async def sensitive_operation(data: SomeInput, current_user: dict = Depends(require_admin_and_owner)):
    """Only users who are both admins and owners can perform this operation"""
    # ... implementation ...


@router.get("/less-sensitive-operation")
async def less_sensitive_operation(current_user: dict = Depends(require_admin_or_owner)):
    """Users who are either admins OR owners can perform this operation"""
    # ... implementation ...

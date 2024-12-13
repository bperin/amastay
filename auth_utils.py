from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any, Callable, List
from functools import wraps
import os
import jwt
from jwt import PyJWTError

app = FastAPI()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"
SUPABASE_URL = os.getenv("SUPABASE_URL")

# We will use HTTPBearer for token extraction
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme.",
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            audience="authenticated",
            issuer=f"{SUPABASE_URL}/auth/v1",
        )

        role = payload.get("role")
        if role != "authenticated":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid role.")

        current_user = {"id": payload.get("sub"), "role": role, "user_type": payload.get("user_metadata", {}).get("user_type", None)}

        return current_user

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT token has expired.")
    except jwt.InvalidAudienceError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid audience.")
    except jwt.InvalidIssuerError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid issuer.")
    except PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid JWT token: {str(e)}")


def get_current_user_id(current_user: dict) -> str:
    """Extract user ID from the current user dict"""
    return current_user["id"]


def require_role(*allowed_roles: str):
    """
    Decorator to check if the user has one of the allowed roles

    Usage:
        @require_role("admin")
        @router.get("/admin-only")
        async def admin_endpoint():
            return {"message": "Admin access granted"}
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from the dependency injection
            current_user = kwargs.get("current_user")
            if not current_user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

            user_type = current_user.get("user_type")
            if not user_type or user_type not in allowed_roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Access denied. Required roles: {', '.join(allowed_roles)}")

            return await func(*args, **kwargs)

        # Add current_user as a dependency
        wrapper.__dependencies__ = [Depends(get_current_user)]
        return wrapper

    return decorator


# Example usage decorators
require_admin = require_role("admin")
require_owner = require_role("owner")
require_manager = require_role("manager")


def require_roles(roles: List[str], require_all: bool = False):
    """
    Create a dependency that checks if the user has the specified roles

    Args:
        roles: List of required roles
        require_all: If True, user must have all roles. If False, any one role is sufficient.
    """

    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        user_type = current_user.get("user_type")
        if not user_type:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User type not found")

        if require_all:
            has_permission = all(role in user_type for role in roles)
        else:
            has_permission = any(role in user_type for role in roles)

        if not has_permission:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Access denied. Required roles: {', '.join(roles)}")
        return current_user

    return role_checker


# Example usage:
require_admin_and_owner = require_roles(["admin", "owner"], require_all=True)
require_admin_or_owner = require_roles(["admin", "owner"], require_all=False)
require_admin = require_roles(["admin"], require_all=True)

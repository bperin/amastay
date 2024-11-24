import jwt
import os
import logging
from flask import request, jsonify, g
from functools import wraps
from datetime import datetime, timezone
from supabase_utils import supabase_client
from supabase import create_client, Client

from dotenv import load_dotenv

load_dotenv()  # Ensure environment variables are loaded

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"  # Supabase uses HS256 by default
SUPABASE_URL = os.getenv("SUPABASE_URL")

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("Missing or invalid JWT token")
            return jsonify({"error": "Missing or invalid JWT token"}), 401

        jwt_token = auth_header.split(" ")[1]

        try:
            # Decode and verify the JWT token with audience and issuer
            payload = jwt.decode(
                jwt_token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM],
                audience="authenticated",
                issuer=f"{SUPABASE_URL}/auth/v1",
            )
            logger.debug(f"JWT Payload: {payload}")

            # Check if the role is 'authenticated'
            role = payload.get("role")
            if role != "authenticated":
                logger.warning("Invalid role")
                return {"error": "Invalid role"}, 403

            # Note: We don't need to manually check for token expiration
            # jwt.decode() will raise jwt.ExpiredSignatureError if the token has expired

            # After successful JWT validation, set up Supabase session
            refresh_token = request.headers.get("x-refresh-token")

            # Store user information in Flask's `g` object
            g.current_user = {
                "id": payload.get("sub"),
                "role": role,
            }
            g.user_id = payload.get("sub")

        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            return {"error": "JWT Token has expired"}, 401
        except jwt.InvalidAudienceError:
            logger.error("Invalid audience")
            return {"error": "Invalid audience"}, 401
        except jwt.InvalidIssuerError:
            logger.error("Invalid issuer")
            return {"error": "Invalid issuer"}, 401
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid JWT token: {str(e)}")
            return {"error": "Invalid JWT token", "message": str(e)}, 401
        except Exception as e:
            logger.exception(f"Unexpected error in jwt_required: {str(e)}")
            return {"error": "An unexpected error occurred"}, 500

        return f(*args, **kwargs)

    return decorated

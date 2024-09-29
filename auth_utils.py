import jwt
import os
from flask import request, jsonify, g
from functools import wraps
from datetime import datetime, timezone
from supabase_utils import supabase_client

from dotenv import load_dotenv

load_dotenv()  # Ensure environment variables are loaded

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = "HS256"  # Supabase uses HS256 by default
SUPABASE_URL = os.getenv("SUPABASE_URL")


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
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

            session = supabase_client.auth.get_session
            print(session)

            # Check if the token has expired
            exp = payload.get("exp")
            if exp and datetime.now(timezone.utc).timestamp() > exp:
                return jsonify({"error": "Token has expired"}), 401

            # Check if the role is 'authenticated'
            role = payload.get("role")
            if role != "authenticated":
                return jsonify({"error": "Invalid role"}), 403

            # Store user information in Flask's `g` object
            g.current_user = {
                "id": payload.get("sub"),  # User's unique identifier
                "email": payload.get("email"),
                "role": payload.get("role"),
                "phone": payload.get("phone"),
                # Add other fields from payload as needed
            }

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidAudienceError:
            return jsonify({"error": "Invalid audience"}), 401
        except jwt.InvalidIssuerError:
            return jsonify({"error": "Invalid issuer"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": "Invalid JWT token", "message": str(e)}), 401

        return f(*args, **kwargs)

    return decorated

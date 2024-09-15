from flask import request, jsonify
from functools import wraps
from supabase_utils import supabase_client

class JwtService:
    
    @staticmethod
    def jwt_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            auth_header = request.headers.get('Authorization')

            if not auth_header or not auth_header.startswith("Bearer "):
                return jsonify({"error": "Missing or invalid JWT token"}), 401

            jwt_token = auth_header.split(" ")[1]

            # Call get_session to verify the session with the token
            session = supabase_client.auth.get_session()

            if session is None or session.access_token != jwt_token:
                return jsonify({"error": "Invalid or expired JWT token"}), 401

            return f(*args, **kwargs)

        return decorated

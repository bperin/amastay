from functools import wraps
from flask import request, jsonify, g
from supabase_utils import supabase_client

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header:
            return jsonify({'error': 'Authorization header is missing!'}), 403

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({'error': 'Authorization header must be in the format: Bearer <token>'}), 403

        token = parts[1]

        try:
            # Use Supabase's method to verify the JWT
            user = supabase_client.auth.api.get_user(token)
            if user.error:
                return jsonify({'error': 'Invalid access token!'}), 403

            # Attach user information to the global context
            g.user = user.user
        except Exception as e:
            return jsonify({'error': 'Token verification failed!', 'details': str(e)}), 403

        return f(*args, **kwargs)
    
    return decorated

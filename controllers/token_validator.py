import jwt
from flask import request, jsonify
from functools import wraps

SECRET_KEY = "Z3XnLfQlD4BITwunu8Q/mrda+/lmDWnV54DfBt9GHpsZJVvhfrAAHU8gHJx1ql5trKvTxLPF2AM+F0oZKZO4Vg=="  # Replace with your actual secret key

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Access token is missing!'}), 403

        try:
            # Remove 'Bearer ' from the token
            token = token.replace('Bearer ', '')
            # Decode the token (replace 'your_secret_key' with your actual secret)
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Access token has expired!'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid access token!'}), 403

        # If token is valid, proceed to the route
        return f(*args, **kwargs)
    return decorated

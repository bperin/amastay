from flask import Blueprint, jsonify

# Define the Blueprint with no full URL path yet
health_bp = Blueprint('health', __name__)

@health_bp.route('/', methods=['GET'])
def health_check():
    """
    Health check endpoint that returns the status of the service.
    """
    return jsonify({"status": "healthy", "message": "Service is running"}), 200

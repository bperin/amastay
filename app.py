# app.py

import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_restx import Api
import json

# Load environment variables
load_dotenv(override=True)

# Import controllers and utilities
from controllers.auth_controller import ns_auth
from controllers.property_controller import ns_property
from controllers.webhook_controller import ns_webhooks
from controllers.health_controller import ns_health
from controllers.model_controller import ns_model
from controllers.booking_controller import ns_booking
from controllers.guest_controller import ns_guest
from controllers.manager_controller import ns_manager
from controllers.user_controller import ns_user
from controllers.team_controller import ns_team
from auth_utils import jwt_required
from services.sagemaker_service import SageMakerService
from services.bedrock_service import BedrockService

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"))
app.logger.addHandler(file_handler)


# Configure JSON encoder/decoder to handle datetime
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


app.json_encoder = CustomJSONEncoder


# Update these lines
app.config["RESTX_JSON"] = {"cls": CustomJSONEncoder}  # Add this line for Flask-RESTX

# Initialize Flask-RESTX API with Swagger UI
api = Api(app, version="0.1", title="Amastay API", description="Amastay API", doc="/swagger")


def create_app():
    """Create and configure the Flask application"""
    # Initialize services
    # try:
    #     SageMakerService.initialize()
    #     app.logger.info("SageMaker service initialized successfully")
    # except Exception as e:
    #     app.logger.error(f"Failed to initialize SageMaker service: {str(e)}")
    #     raise

    try:
        BedrockService.initialize()
        app.logger.info("Bedrock service initialized successfully")
    except Exception as e:
        app.logger.error(f"Failed to initialize Bedrock service: {str(e)}")
        raise
    # Register Namespaces with the API
    api.add_namespace(ns_auth, path="/api/v1/auth")
    api.add_namespace(ns_property, path="/api/v1/properties")
    api.add_namespace(ns_booking, path="/api/v1/bookings")
    api.add_namespace(ns_guest, path="/api/v1/guests")
    api.add_namespace(ns_health, path="/api/v1/health")
    api.add_namespace(ns_webhooks, path="/api/v1/webhooks")
    api.add_namespace(ns_model, path="/api/v1/model")
    api.add_namespace(ns_manager, path="/api/v1/managers")
    api.add_namespace(ns_user, path="/api/v1/users")
    api.add_namespace(ns_team, path="/api/v1/teams")

    return app


# Create the application instance
app = create_app()


@app.route("/api/v1/debug/env", methods=["GET"])
def debug_env():
    # Only enable in non-production environments
    if os.getenv("FLASK_ENV") != "production":
        return {"environment": os.getenv("FLASK_ENV"), "system_phone": os.getenv("SYSTEM_PHONE_NUMBER"), "log_level": os.getenv("LOG_LEVEL")}
    return {"error": "Debug endpoint not available in production"}, 403


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)

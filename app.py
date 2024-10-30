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
load_dotenv()

# Import controllers and utilities
from controllers.auth_controller import ns_auth
from controllers.property_controller import ns_property
from controllers.webhook_controller import ns_webhooks
from controllers.health_controller import ns_health
from controllers.model_controller import ns_model
from controllers.booking_controller import ns_booking
from auth_utils import jwt_required

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

# Register Namespaces with the API
api.add_namespace(ns_auth, path="/api/v1/auth")
api.add_namespace(ns_property, path="/api/v1/properties")
api.add_namespace(ns_booking, path="/api/v1/bookings")
api.add_namespace(ns_health, path="/api/v1/health")
api.add_namespace(ns_webhooks, path="/api/v1/webhooks")
api.add_namespace(ns_model, path="/api/v1/model")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)

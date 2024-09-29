# app.py

import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables before imports

import logging
from flask import Flask, jsonify, g
from flask_cors import CORS
from flask_restx import Api
from controllers.auth_controller import auth_bp
from controllers.property_controller import property_bp
from controllers.scraper_controller import ns_scraper
from controllers.sms_controller import sms_bp
from controllers.ai_controller import ai_bp
from controllers.health_controller import health_bp
from controllers.sagemaker_controller import sagemaker_bp
from auth_utils import jwt_required


app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)
app.logger.addHandler(file_handler)

# Initialize Flask-RESTX API
api = Api(app, version="1.0", title="Your API", description="A simple API")


# Protected route example
@app.route("/protected", methods=["GET"])
@jwt_required
def protected_route():
    user_email = g.current_user.get("email") or g.current_user.get("phone")
    return jsonify({"message": f"Hello {user_email}! This is a protected route."}), 200


# Register Blueprints with unique prefixes
app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
app.register_blueprint(property_bp, url_prefix="/api/v1/properties")
app.register_blueprint(sms_bp, url_prefix="/api/v1/sms")
app.register_blueprint(ai_bp, url_prefix="/api/v1/ai")
app.register_blueprint(health_bp, url_prefix="/api/v1/health")
app.register_blueprint(sagemaker_bp, url_prefix="/api/v1/sagemaker")

# Register Namespace with the API
api.add_namespace(ns_scraper, path="/api/v1/scraper")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)

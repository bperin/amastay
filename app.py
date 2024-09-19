# app.py

import logging
from flask import Flask
from flask_cors import CORS
from flask_restx import Api, Resource
from controllers.auth_controller import auth_bp
from controllers.property_controller import property_bp
from controllers.scraper_controller import ns_scraper  # Assuming this is a Namespace
from controllers.sms_controller import sms_bp
from controllers.ai_controller import ai_bp
from controllers.health_controller import health_bp  # Import the health blueprint

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

# Initialize Flask-RESTX API
api = Api(app, version='1.0', title='Your API', description='A simple API')

# Register Blueprints with appropriate prefixes
app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
app.register_blueprint(property_bp, url_prefix='/api/v1')
app.register_blueprint(sms_bp, url_prefix='/api/v1')
app.register_blueprint(ai_bp, url_prefix='/api/v1')
app.register_blueprint(health_bp, url_prefix='/api/v1')  # Register health blueprint

# Register Namespace with the API
api.add_namespace(ns_scraper)  # Correctly add ns_scraper to the API

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
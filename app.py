# app.py

import logging
from flask import Flask, jsonify
from flask_cors import CORS
from flask_restx import Api, Resource
from controllers.auth_controller import auth_bp
from controllers.property_controller import property_bp
from controllers.scraper_controller import ns_scraper  # Assuming this is a Namespace
from controllers.sms_controller import sms_bp
from controllers.ai_controller import ai_bp
from controllers.health_controller import health_bp
from controllers.token_validator import token_required  # Import the health blueprint

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)
app.logger.addHandler(file_handler)

# Initialize Flask-RESTX API
api = Api(app, version='1.0', title='Your API', description='A simple API')

@app.route('/protected', methods=['GET'])
@token_required
def protected_route():
    return jsonify({"message": f"Hello {g.user.email}! This is a protected route."}), 200

# Example of a public route
@app.route('/public', methods=['GET'])
def public_route():
    return jsonify({"message": "This is a public route. No authentication required."}), 200


# Register Blueprints with appropriate prefixes
app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
app.register_blueprint(property_bp, url_prefix='/api/v1')
app.register_blueprint(sms_bp, url_prefix='/api/v1')
app.register_blueprint(ai_bp, url_prefix='/api/v1')
app.register_blueprint(health_bp, url_prefix='/api/v1')  # Register health blueprint

# Register Namespace with the API
api.add_namespace(ns_scraper)  # Correctly add ns_scraper to the API

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
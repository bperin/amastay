import logging
from flask import Flask, request
from flask_cors import CORS
from flask_restx import Api, Resource
from controllers.auth_controller import auth_bp  # Import the auth blueprint
from controllers.property_controller import PropertyController
from controllers.scrape_controller import handle_scrape
from controllers.sms_controller import handle_sms_request
from services.jwt_service import JwtService

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

# Initialize Flask-RESTX API (Flask-RESTX, not RESTPlus)
api = Api(app, version='1.0', title='Your API', description='A simple API')

api = Api(app)
ns = api.namespace('api/v1', description='Main API operations')

# Register routes as Flask-RESTX Resources
@ns.route('/scrape')
class ScrapeResource(Resource):
    def post(self):
        """Handles scraping"""
        return handle_scrape(request)

@ns.route('/process_sms')
class ProcessSMSResource(Resource):
    def post(self):
        """Handles SMS requests"""
        return handle_sms_request()

# Property management routes
@app.route('/properties', methods=['POST'])
def create_property():
    """
    Route to create a new property and invoke the scraper if a URL is provided.
    """
    return PropertyController.create_property()

@app.route('/properties', methods=['GET'])
def get_properties():
    """
    Route to fetch all properties.
    """
    return PropertyController.get_properties()

@app.route('/properties/<property_id>', methods=['PUT'])
def update_property(property_id):
    """
    Route to update an existing property by property_id.
    """
    return PropertyController.update_property(property_id)

@app.route('/properties/<property_id>', methods=['DELETE'])
def delete_property(property_id):
    """
    Route to delete a property by property_id.
    """
    return PropertyController.delete_property(property_id)

@ns.route('/hello')
class HelloWorldResource(Resource):
    def get(self):
        """Says hello"""
        return {"message": "world"}

@ns.route('/health')
class HealthResource(Resource):
    def get(self):
        """Checks API health"""
        return {"status": "OK"}, 200  # Returning a dictionary instead of jsonify

# Register the auth blueprint (assuming the auth routes are managed in auth_controller)
app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')

# Initialize API with the namespace
api.add_namespace(ns)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)

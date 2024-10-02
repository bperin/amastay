# app.py

import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()  # Load environment variables before imports

import logging

from flask_cors import CORS
from flask_restx import Api
from controllers.auth_controller import ns_auth
from controllers.property_controller import ns_property
from controllers.scraper_controller import ns_scraper
from controllers.webhook_controller import ns_webhooks
from controllers.health_controller import ns_health
from controllers.model_controller import ns_model
from auth_utils import jwt_required

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
)
file_handler = logging.FileHandler("app.log")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
)
app.logger.addHandler(file_handler)

# Initialize Flask-RESTX API with Swagger UI
api = Api(
    app, version="0.1", title="Amastay API", description="Amastay API", doc="/swagger"
)

# Register Namespace with the API
api.add_namespace(ns_auth, path="/api/v1/auth")
api.add_namespace(ns_property, path="/api/v1/properties")
api.add_namespace(ns_health, path="/api/v1/health")
api.add_namespace(ns_webhooks, path="/api/v1/webhooks")
api.add_namespace(ns_scraper, path="/api/v1/scraper")
api.add_namespace(ns_model, path="/api/v1/model")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)

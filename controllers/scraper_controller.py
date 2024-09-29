from flask_restx import Resource, Namespace
from services.scraper_service import ScraperService
from flask import request, jsonify
import uuid

# Define a namespace for Scraper
ns_scraper = Namespace("scraper", description="Scraping operations")


@ns_scraper.route("/scrape")
class ScrapeResource(Resource):
    def post(self):
        """
        Handles scraping requests and processes the URL provided in the request.
        """
        data = request.get_json()
        url = data.get("url")

        # Generate a unique property ID
        property_id = str(uuid.uuid4())

        # Validate URLe
        if not url:
            return {"error": "URL is missing"}, 400

        # Call the service to scrape the data and handle file upload and storage
        try:
            response = ScraperService.scrape_and_save(url, property_id)
            return jsonify(response), 200 if "message" in response else 500
        except Exception as e:
            return {"error": str(e)}, 500

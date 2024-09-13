# app.py
from flask import Flask, request, jsonify
from scraper import Scraper
from utils import supabase  # Assuming utils.py contains Supabase configuration
import uuid

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape_property():
    data = request.get_json()
    url = data.get('url')
    property_id = str(uuid.uuid4())  # Generate a unique ID for the property

    if not url:
        return jsonify({"error": "URL is missing"}), 400

    try:
        # Scrape the data using the Scraper class
        scraper = Scraper(url)
        scraped_content = scraper.scrape()

        if not scraped_content:
            return jsonify({"error": "Failed to scrape the data"}), 500

        # Upload the scraped content to Supabase storage
        storage_response = scraper.upload_document_to_supabase(property_id, scraped_content)

        if not storage_response:
            return jsonify({"error": "Failed to upload the scraped document"}), 500

        # Store the scraped document metadata in the database
        db_response = scraper.save_document_to_database(property_id, scraped_content)

        return jsonify({
            "message": "Scraping and file upload successful",
            "property_id": property_id,
            "storage_response": storage_response,
            "db_response": db_response.data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

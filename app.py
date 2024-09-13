# app.py
from flask import Flask, request, jsonify
from utils import supabase, scrape_property_data  # Assuming utils.py contains these

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"error": "URL is missing"}), 400

    try:
        # Scrape the property data
        scraped_data = scrape_property_data(url)

        # Insert scraped data into Supabase (assuming 'properties' table)
        supabase_response = supabase.table('properties').insert(scraped_data).execute()

        return jsonify({
            "message": "Scraping and insertion successful",
            "scraped_data": scraped_data,
            "supabase_response": supabase_response.data
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

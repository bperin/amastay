import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from controllers.auth_controller import AuthController
from controllers.property_controller import PropertyController
from controllers.scrape_controller import handle_scrape
from controllers.chat_controller import handle_chat
from controllers.sms_controller import handle_sms_request
from services.jwt_service import JwtService

app = Flask(__name__)

CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

@app.route('/scrape', methods=['POST'])
def scrape():
    return handle_scrape(request)

@app.route('/chat', methods=['POST'])
def chat():
    return handle_chat(request)

@app.route('/process_sms', methods=['POST'])
def process_sms():
    return handle_sms_request()

# Protect these endpoints using @JwtService.jwt_required decorator
@app.route('/properties', methods=['POST'])
@JwtService.jwt_required
def create_property():
    return PropertyController.create_property(request)

@app.route('/properties', methods=['GET'])
@JwtService.jwt_required
def get_properties():
    return PropertyController.get_properties()

@app.route('/hello', methods=['GET'])
def hello():
    return "world"

@app.route('/health', methods=['GET'])
def process_health():
    return jsonify(status="OK"), 200

# Route for sending OTP
@app.route('/send_otp', methods=['POST'])
def send_otp():
    return AuthController.send_otp(request)

# Route for verifying OTP
@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    return AuthController.verify_otp(request)

# Refresh token route
@app.route('/refresh_token', methods=['POST'])
def refresh_token():
    return AuthController.refresh_token(request)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)

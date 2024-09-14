from flask import Flask, request, jsonify
from controllers.auth_controller import AuthController
from controllers.property_controller import PropertyController
from controllers.scrape_controller import handle_scrape
from controllers.chat_controller import handle_chat
from controllers.sms_controller import handle_sms_request

app = Flask(__name__)

@app.route('/scrape', methods=['POST'])
def scrape():
    return handle_scrape(request)

@app.route('/chat', methods=['POST'])
def chat():
    return handle_chat(request)

@app.route('/process_sms', methods=['POST'])
def process_sms():
    return handle_sms_request()

@app.route('/properties', methods=['POST'])
def create_property():
    return PropertyController.create_property(request)

@app.route('/properties', methods=['GET'])
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

if __name__ == "__main__":
    app.run(debug=True)

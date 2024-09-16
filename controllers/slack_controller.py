import os
import logging
from flask import Blueprint, request, jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import hashlib
import hmac
import time
from chat_service import query_model  # Import the model querying logic

# Set your Slack bot token and signing secret as environment variables
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')

# Initialize the Slack client
slack_client = WebClient(token=SLACK_BOT_TOKEN)

# Create a blueprint for Slack-related routes
slack_bp = Blueprint('slack_bp', __name__)

# Function to verify Slack signature
def verify_slack_request(request):
    timestamp = request.headers.get('X-Slack-Request-Timestamp')
    if abs(time.time() - float(timestamp)) > 60 * 5:
        return False
    
    sig_basestring = 'v0:' + timestamp + ':' + request.get_data(as_text=True)
    my_signature = 'v0=' + hmac.new(
        SLACK_SIGNING_SECRET.encode('utf-8'),
        sig_basestring.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    slack_signature = request.headers.get('X-Slack-Signature')
    return hmac.compare_digest(my_signature, slack_signature)

@slack_bp.route('/slack/events', methods=['POST'])
def slack_events():
    if not verify_slack_request(request):
        return "Request verification failed", 403

    data = request.json
    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})

    event = data.get('event', {})
    
    if event.get('type') == 'message' and 'bot_id' not in event:
        user_message = event.get('text')
        channel_id = event.get('channel')

        # Query the SageMaker model with the user's input
        ai_response = query_model(user_message)

        try:
            slack_client.chat_postMessage(channel=channel_id, text=ai_response)
        except SlackApiError as e:
            logging.error(f"Error posting message: {e.response['error']}")

    return jsonify({'status': 'ok'})

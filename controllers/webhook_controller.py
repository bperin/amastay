import logging
from flask import Blueprint, Flask, request, jsonify
from services.process_service import ProcessService

# Create logger instance
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

wh_bp = Blueprint("webhook_bp", __name__)


@wh_bp.route("/sms", methods=["POST"])
def sms_webhook():
    try:
        # Log incoming request
        logger.info("Received webhook request: %s", request.json)

        data = request.json
        origination_number = data.get("OriginationNumber")
        message_body = data.get("MessageBody")
        sms_id = data.get("MessageId")  # AWS Pinpoint message ID

        # Log incoming SMS data
        logger.info(
            "Processing SMS - Origination Number: %s, Message Body: %s, Message ID: %s",
            origination_number,
            message_body,
            sms_id,
        )

        # Delegate to the ProcessService
        ProcessService.handle_incoming_sms(sms_id, origination_number, message_body)

        # Log successful processing
        logger.info("SMS processed successfully for Message ID: %s", sms_id)

        # Return a success response to AWS Pinpoint
        return jsonify({"status": "success"}), 200

    except Exception as e:
        # Log any exceptions
        logger.error("Error processing webhook: %s", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500

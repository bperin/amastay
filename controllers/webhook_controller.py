import logging
from flask import request
from flask_restx import Namespace, Resource, fields
from services.process_service import handle_incoming_sms

# Create logger instance
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ns_webhooks = Namespace("webhooks", description="Webhook for receiving SMS")

# Define models for request/response
sms_model = ns_webhooks.model(
    "lambda_sms",
    {
        "phone": fields.String(required=True, description="The phone number that sent the message"),
        "message": fields.String(required=True, description="The content of the SMS message"),
        "message_id": fields.String(required=True, description="AWS Pinpoint message ID"),
    },
)


@ns_webhooks.route("/sms")
class SMSWebhook(Resource):

    @ns_webhooks.doc("sms_webhook")
    @ns_webhooks.expect(sms_model)
    def post(self):
        """
        Receives and processes incoming SMS webhooks.
        """
        try:
            data = request.json
            origination_number = data.get("phone")
            message_body = data.get("message")
            message_id = data.get("message_id")

            handle_incoming_sms(message_id, origination_number, message_body, true)

            return {"status": "success"}, 200

        except Exception as e:
            logger.error("Error processing webhook: %s", str(e))
            return {"status": "error", "message": str(e)}, 500

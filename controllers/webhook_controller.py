import logging
from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from services.process_service import ProcessService

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

response_model = ns_webhooks.model(
    "Response",
    {"status": fields.String(description="Status of the webhook processing")},
)


@ns_webhooks.route("/sms")
class SMSWebhook(Resource):

    @ns_webhooks.doc("sms_webhook")
    @ns_webhooks.expect(sms_model)
    @ns_webhooks.marshal_with(response_model, code=200)
    def post(self):
        """
        Receives and processes incoming SMS webhooks.
        """
        try:
            # Log incoming request
            logger.info("Received webhook request: %s", request.json)

            data = request.json
            origination_number = data.get("phone")
            message_body = data.get("message")
            sms_id = data.get("sms_id")  # AWS Pinpoint message ID

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
            return {"status": "success"}, 200

        except Exception as e:
            # Log any exceptions
            logger.error("Error processing webhook: %s", str(e))
            return {"status": "error", "message": str(e)}, 500

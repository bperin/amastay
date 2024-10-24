import logging
import os
import tempfile
import time
from services.booking_service import BookingService
from services.message_service import MessageService
from services.pinpoint_service import PinpointService
from services.documents_service import DocumentsService
from services.property_information_service import PropertyInformationService
from services.property_service import PropertyService
from services.model_service import ModelService
from supabase_utils import supabase_client


class ProcessService:
    model_service = ModelService()

    @staticmethod
    def handle_incoming_sms(sms_id, origination_number, message_body):
        """
        Handles incoming SMS between a guest and the AI.
        Retrieves guest information for sender_id, saves the guest message before querying history,
        and saves the AI response after generating it.
        """
        try:
            if ProcessService.is_message_from_ai(origination_number):
                logging.info(f"Message from AI, ignoring: {message_body}")
                return

            from services.guest_service import GuestService

            guest = GuestService.get_guest_by_phone(origination_number)
            if not guest:
                logging.warning(f"No guest found for phone number {origination_number}")
                error_message = (
                    "We couldn't find your information. Please contact support."
                )
                PinpointService.send_sms(
                    origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message
                )
                return

            booking = BookingService.get_next_booking_by_guest_id(guest.id)
            if not booking:
                error_message = "We couldn't find any upcoming bookings for you. Please check your details."
                PinpointService.send_sms(
                    origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message
                )
                logging.warning(
                    f"No upcoming bookings for phone number {origination_number}"
                )
                return

            property = PropertyService.get_property_by_booking_id(booking.property_id)

            if not property:
                logging.warning(f"No property found for booking ID {booking.id}")
                error_message = "We're sorry, but we couldn't find the property associated with your booking. Please contact support."
                PinpointService.send_sms(
                    origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message
                )
                return

            property_information = PropertyInformationService.get_property_information(
                property.id
            )
            if not property_information:
                logging.info(
                    f"No property information found for property ID {property.id}"
                )
            else:
                logging.info(
                    f"Retrieved property information for property ID {property.id}"
                )

            property_documents = DocumentsService.get_documents_by_property_id(
                property.id
            )

            if not property_documents:
                logging.info(f"No documents found for property ID {property.id}")
            else:
                logging.info(
                    f"Retrieved {len(property_documents)} documents for property ID {property.id}"
                )

            processed_documents = []
            all_document_text = ""
            if property_documents:
                for document in property_documents:
                    try:
                        plain_text = DocumentsService.read_document(
                            document["file_url"]
                        )
                        if plain_text:
                            processed_documents.append(
                                {"name": document["file_url"], "content": plain_text}
                            )
                            all_document_text += plain_text + "\n\n"
                        else:
                            logging.warning(
                                f"Could not read content for document: {document['file_url']}"
                            )
                    except Exception as doc_error:
                        logging.error(
                            f"Error processing document {document['file_url']}: {str(doc_error)}"
                        )

                logging.info(
                    f"Processed {len(processed_documents)} documents for property ID {property.id}"
                )
            else:
                logging.info("No property documents to process")
            breakpoint()
            ai_response = ProcessService.model_service.query_model(
                booking,
                property,
                guest,
                message_body,
                property_information,
                all_document_text,
            )

            PinpointService.send_sms(
                origination_number,
                os.getenv("SYSTEM_PHONE_NUMBER"),
                ai_response["response"],
            )

        except Exception as e:
            logging.error(f"Error processing incoming SMS: {str(e)}")
            error_message = "We're sorry, but there was an error processing your message. Please try again later."
            PinpointService.send_sms(
                origination_number, os.getenv("SYSTEM_PHONE_NUMBER"), error_message
            )

    @staticmethod
    def is_message_from_ai(origination_number: str) -> bool:
        ai_number = os.getenv("SYSTEM_PHONE_NUMBER")
        return origination_number == ai_number

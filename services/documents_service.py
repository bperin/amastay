import os
import tempfile
import time
from supabase_utils import supabase_client
import logging


class DocumentsService:
    BUCKET_NAME = "properties"

    @staticmethod
    def save_scraped_data(property_id, scraped_data):
        """Save scraped data as a text file to Supabase storage."""
        filename = f"{property_id}_{int(time.time())}.txt"
        try:
            with tempfile.NamedTemporaryFile(
                delete=False, mode="w", encoding="utf-8"
            ) as temp_file:
                temp_file.write(scraped_data)
                temp_file_path = temp_file.name

            # Upload to Supabase
            with open(temp_file_path, "rb") as file:
                response = supabase_client.storage.from_(
                    DocumentsService.BUCKET_NAME
                ).upload(
                    file=file,
                    path=filename,
                    file_options={"content-type": "text/plain"},
                )

            if response:
                logging.info(f"Document uploaded successfully as {filename}")
                os.remove(temp_file_path)  # Clean up temp file
                return filename
            else:
                logging.error(f"Failed to upload document to Supabase.")
                return None
        except Exception as e:
            logging.error(f"Error uploading document: {e}")
            return None

    @staticmethod
    def get_documents_by_property_id(property_id):
        """Fetch all documents for a given property ID."""
        try:
            response = (
                supabase_client.table("documents")
                .select("*")
                .eq("property_id", str(property_id))
                .execute()
            )
            if response.data:
                return [
                    {"id": doc["id"], "file_url": doc["file_url"]}
                    for doc in response.data
                ]
            else:
                return []
        except Exception as e:
            logging.error(f"Error fetching documents for property {property_id}: {e}")
            return []

    @staticmethod
    def read_document(filename):
        """Read a document from storage and return its content as plain text."""
        try:
            response = supabase_client.storage.from_(
                DocumentsService.BUCKET_NAME
            ).download(filename)
            return response.decode("utf-8")
        except Exception as e:
            logging.error(f"Error reading document {filename}: {e}")
            return None

    @staticmethod
    def delete_document(filename):
        """Delete a document from storage."""
        try:
            supabase_client.storage.from_(DocumentsService.BUCKET_NAME).remove(
                [filename]
            )
            logging.info(f"Document {filename} deleted successfully")
            return True
        except Exception as e:
            logging.error(f"Error deleting document {filename}: {e}")
            return False

    @staticmethod
    def update_document(property_id, new_content):
        """Update the document for a property with new content."""
        # First, get the existing documents for this property
        existing_docs = DocumentsService.get_documents_by_property_id(property_id)

        # If there are existing documents, delete them
        for doc in existing_docs:
            DocumentsService.delete_document(doc)

        # Now save the new content
        return DocumentsService.save_scraped_data(property_id, new_content)

import os
import tempfile
import time
from typing import List
from models.document_model import Document
from supabase_utils import supabase_client, supabase_admin_client
import logging


class DocumentsService:
    BUCKET_NAME = "properties"

    @staticmethod
    def get_documents_by_property_id(property_id: str) -> List[Document]:
        """Fetch all documents for a given property ID."""
        try:
            document_query = supabase_client.from_("documents").select("*").eq("property_id", property_id).execute()

            if not document_query.data:
                logging.error(f"No documents found for property_id: {property_id}")
                raise ValueError(f"No documents found for property_id: {property_id}")

            documents = []
            for doc in document_query.data:
                documents.append(Document(**doc))

            return documents
        except Exception as e:
            logging.error(f"Error fetching documents for property {property_id}: {e}")
            raise e

    @staticmethod
    def delete_document(filename: str) -> bool:
        """Delete a document from storage."""
        try:
            supabase_client.storage.from_(DocumentsService.BUCKET_NAME).remove([filename])
            logging.info(f"Document {filename} deleted successfully")
            return True
        except Exception as e:
            logging.error(f"Error deleting document {filename}: {e}")
            return False

import logging
from google.cloud import discoveryengine_v1beta


class VertexSearchService:
    """Service for managing Vertex AI Search operations"""

    PROJECT_ID = "amastay"
    LOCATION = "us-central1"
    SEARCH_ENGINE_ID = "your-search-engine-id"  # You'll need to set this
    SERVICE_ACCOUNT_PATH = "amastay/amastay_service_account.json"

    @staticmethod
    async def update_property_index(property_id: str) -> None:
        """Updates Vertex AI search index with property document"""
        try:
            # Initialize Vertex Search client with credentials
            client = discoveryengine_v1beta.DocumentServiceClient.from_service_account_json(VertexSearchService.SERVICE_ACCOUNT_PATH)

            # Format the parent resource name
            parent = client.branch_path(project=VertexSearchService.PROJECT_ID, location=VertexSearchService.LOCATION, data_store=VertexSearchService.SEARCH_ENGINE_ID, branch="default_branch")

            # Create document
            document = discoveryengine_v1beta.Document(id=f"property_{property_id}", content={"uri": f"gs://amastay_property_data_text/{property_id}.txt", "mime_type": "text/plain"})

            request = discoveryengine_v1beta.ImportDocumentsRequest(parent=parent, documents=[document], reconciliation_mode=discoveryengine_v1beta.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL)

            operation = client.import_documents(request=request)
            result = operation.result()  # Waits for operation to complete

            logging.info(f"Successfully updated search index for property {property_id}")
            return result

        except Exception as e:
            logging.error(f"Failed to update Vertex search index: {e}")
            raise

import logging
from google.cloud import discoveryengine_v1beta
from google.cloud import storage
import asyncio


class VertexSearchService:
    """Service for managing Vertex AI Search operations"""

    PROJECT_ID = "amastay"
    LOCATION = "us-central1"
    SEARCH_ENGINE_ID = "amastay-ds-property-text_1735943367196"  # This matches the vector_store_id in LlamaService
    SERVICE_ACCOUNT_PATH = "amastay/amastay_service_account.json"

    @staticmethod
    async def _check_file_exists(bucket_name: str, file_path: str) -> bool:
        """Check if file exists in GCS bucket"""
        try:
            storage_client = storage.Client.from_service_account_json(VertexSearchService.SERVICE_ACCOUNT_PATH)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(file_path)
            return blob.exists()
        except Exception as e:
            logging.error(f"Error checking file existence: {e}")
            return False

    @staticmethod
    async def update_property_index(property_id: str) -> None:
        """Updates Vertex AI search index with property document"""
        try:
            # Check if file exists in GCS
            file_path = f"{property_id}.txt"
            bucket_name = "amastay_property_data_text"

            # Retry up to 3 times with 2 second delays
            for attempt in range(3):
                if await VertexSearchService._check_file_exists(bucket_name, file_path):
                    break
                if attempt < 2:  # Don't sleep on last attempt
                    await asyncio.sleep(2)
            else:
                raise FileNotFoundError(f"File {file_path} not found in bucket {bucket_name}")

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

    @staticmethod
    async def search_properties(query: str, property_ids: list[str] = None) -> dict:
        """
        Search for properties with optional filtering by property IDs
        """
        try:
            client = discoveryengine_v1beta.SearchServiceClient.from_service_account_json(
                VertexSearchService.SERVICE_ACCOUNT_PATH
            )
            
            # Format the parent resource name
            parent = client.branch_path(
                project=VertexSearchService.PROJECT_ID,
                location=VertexSearchService.LOCATION,
                data_store=VertexSearchService.SEARCH_ENGINE_ID,
                branch="default_branch"
            )

            # Build filter if property_ids provided
            filter_str = ""
            if property_ids:
                # Create OR condition for multiple property IDs
                id_conditions = [f"id = 'property_{pid}'" for pid in property_ids]
                filter_str = " OR ".join(id_conditions)

            # Create search request
            request = discoveryengine_v1beta.SearchRequest(
                parent=parent,
                query=query,
                filter=filter_str if filter_str else None,
                page_size=10
            )

            response = client.search(request)
            return response

        except Exception as e:
            logging.error(f"Failed to search properties: {e}")
            raise

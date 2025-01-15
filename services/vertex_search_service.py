import logging
from google.cloud import discoveryengine_v1beta
from google.cloud import storage
import asyncio
from typing import Optional


class VertexSearchService:
    """Service for managing Vertex AI Search operations"""

    PROJECT_ID = "amastay"
    LOCATION = "us-central1"
    SEARCH_ENGINE_ID = "amastay-ds-property-text_1735943367196"
    SERVICE_ACCOUNT_PATH = "amastay/amastay_service_account.json"
    MAX_RETRIES = 3
    RETRY_DELAY = 2

    @staticmethod
    async def _check_file_exists(bucket_name: str, file_path: str) -> bool:
        """
        Check if file exists in GCS bucket with retries
        Returns True if file exists, False otherwise
        """
        try:
            storage_client = storage.Client.from_service_account_json(VertexSearchService.SERVICE_ACCOUNT_PATH)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(file_path)
            return blob.exists()
        except Exception as e:
            logging.error(f"Error checking file existence: {e}")
            return False

    @staticmethod
    async def _wait_for_file(bucket_name: str, file_path: str) -> bool:
        """
        Wait for file to appear in GCS with exponential backoff
        Returns True if file found within retry limit, False otherwise
        """
        MAX_RETRIES = 5
        INITIAL_DELAY = 2

        for attempt in range(MAX_RETRIES):
            if await VertexSearchService._check_file_exists(bucket_name, file_path):
                logging.info(f"File {file_path} found in bucket {bucket_name} on attempt {attempt + 1}")
                return True

            if attempt < MAX_RETRIES - 1:
                wait_time = INITIAL_DELAY * (2**attempt)
                logging.info(f"File not found, waiting {wait_time}s before retry {attempt + 2}/{MAX_RETRIES}")
                await asyncio.sleep(wait_time)

        logging.error(f"File {file_path} not found in bucket {bucket_name} after {MAX_RETRIES} attempts")
        return False

    @staticmethod
    async def update_property_index(property_id: str) -> Optional[discoveryengine_v1beta.ImportDocumentsResponse]:
        """
        Updates Vertex AI search index with property document
        Waits for file to be available in GCS before updating
        """
        try:
            file_path = f"{property_id}.txt"
            bucket_name = "amastay_property_data_text"

            # Initial delay to allow for GCS consistency
            await asyncio.sleep(3)  # Add initial delay

            # Wait for file to be available in GCS
            if not await VertexSearchService._wait_for_file(bucket_name, file_path):
                logging.error(f"File {file_path} not found in bucket {bucket_name} - checking bucket contents")

                # List bucket contents for debugging
                storage_client = storage.Client.from_service_account_json(VertexSearchService.SERVICE_ACCOUNT_PATH)
                bucket = storage_client.bucket(bucket_name)
                blobs = list(bucket.list_blobs(prefix=file_path))
                if blobs:
                    logging.info(f"Found matching files: {[b.name for b in blobs]}")
                else:
                    logging.info("No matching files found in bucket")

                raise FileNotFoundError(f"File {file_path} not found in bucket {bucket_name}")

            # Initialize Vertex Search client
            client = discoveryengine_v1beta.DocumentServiceClient.from_service_account_json(VertexSearchService.SERVICE_ACCOUNT_PATH)

            parent = client.branch_path(project=VertexSearchService.PROJECT_ID, location=VertexSearchService.LOCATION, data_store=VertexSearchService.SEARCH_ENGINE_ID, branch="default_branch")

            document = discoveryengine_v1beta.Document(id=f"property_{property_id}", content={"uri": f"gs://{bucket_name}/{file_path}", "mime_type": "text/plain"})

            request = discoveryengine_v1beta.ImportDocumentsRequest(parent=parent, documents=[document], reconciliation_mode=discoveryengine_v1beta.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL)

            operation = client.import_documents(request=request)
            result = operation.result()

            logging.info(f"Successfully updated search index for property {property_id}")
            return result

        except Exception as e:
            logging.error(f"Failed to update Vertex search index for property {property_id}: {e}")
            raise

    @staticmethod
    async def search_properties(query: str, property_ids: list[str] = None) -> dict:
        """
        Search for properties with optional filtering by property IDs
        """
        try:
            client = discoveryengine_v1beta.SearchServiceClient.from_service_account_json(VertexSearchService.SERVICE_ACCOUNT_PATH)

            # Format the parent resource name
            parent = client.branch_path(project=VertexSearchService.PROJECT_ID, location=VertexSearchService.LOCATION, data_store=VertexSearchService.SEARCH_ENGINE_ID, branch="default_branch")

            # Build filter if property_ids provided
            filter_str = ""
            if property_ids:
                # Create OR condition for multiple property IDs
                id_conditions = [f"id = 'property_{pid}'" for pid in property_ids]
                filter_str = " OR ".join(id_conditions)

            # Create search request
            request = discoveryengine_v1beta.SearchRequest(parent=parent, query=query, filter=filter_str if filter_str else None, page_size=10)

            response = client.search(request)
            return response

        except Exception as e:
            logging.error(f"Failed to search properties: {e}")
            raise

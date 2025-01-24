import logging
import os
from google.cloud import discoveryengine_v1beta
from google.cloud import storage
from google.api_core.client_options import ClientOptions
import asyncio
from typing import Optional
from google.oauth2 import service_account
import json


class VertexService:
    """Service for managing Vertex AI Search operations"""

    PROJECT_ID = "amastay"
    LOCATION = "global"
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "amastay_service_account.json")
    MAX_RETRIES = 3
    RETRY_DELAY = 2

    @staticmethod
    async def _check_file_exists(bucket_name: str, file_path: str) -> bool:
        """
        Check if file exists in GCS bucket with retries
        Returns True if file exists, False otherwise
        """
        try:
            storage_client = storage.Client.from_service_account_json(VertexService.SERVICE_ACCOUNT_PATH)
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
            if await VertexService._check_file_exists(bucket_name, file_path):
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
            await asyncio.sleep(3)

            # Wait for file to be available in GCS
            if not await VertexService._wait_for_file(bucket_name, file_path):
                logging.error(f"File {file_path} not found in bucket {bucket_name} - checking bucket contents")

                # List bucket contents for debugging
                storage_client = storage.Client.from_service_account_json(VertexService.SERVICE_ACCOUNT_PATH)
                bucket = storage_client.bucket(bucket_name)
                blobs = list(bucket.list_blobs(prefix=file_path))
                if blobs:
                    logging.info(f"Found matching files: {[b.name for b in blobs]}")
                else:
                    logging.info("No matching files found in bucket")
                raise FileNotFoundError(f"File {file_path} not found in bucket {bucket_name}")

            # Set client options for global endpoint
            client_options = ClientOptions(api_endpoint=f"{VertexService.LOCATION}-discoveryengine.googleapis.com") if VertexService.LOCATION != "global" else None

            # Create a client
            client = discoveryengine_v1beta.DocumentServiceClient(client_options=client_options, credentials=service_account.Credentials.from_service_account_file(VertexService.SERVICE_ACCOUNT_PATH))

            # Get the full resource name of the branch
            parent = client.branch_path(project=VertexService.PROJECT_ID, location=VertexService.LOCATION, data_store=VertexService.SEARCH_ENGINE_ID, branch="default_branch")

            # Create import request
            request = discoveryengine_v1beta.ImportDocumentsRequest(parent=parent, gcs_source=discoveryengine_v1beta.GcsSource(input_uris=[f"gs://{bucket_name}/{file_path}"], data_schema="content"), reconciliation_mode=discoveryengine_v1beta.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL)  # For unstructured documents (TXT files)

            # Make the request and wait for completion
            operation = client.import_documents(request=request)
            print(f"Waiting for operation to complete: {operation.operation.name}")
            result = operation.result()

            # Get metadata after operation is complete
            metadata = discoveryengine_v1beta.ImportDocumentsMetadata(operation.metadata)
            logging.info(f"Successfully updated search index for property {property_id}. Metadata: {metadata}")

            return result

        except Exception as e:
            logging.error(f"Failed to update Vertex search index for property {property_id}: {e}")
            raise

    @staticmethod
    async def create_data_store(data_store_id: str) -> str:
        """Create a new data store for property search"""
        try:
            # Create a client
            client = discoveryengine_v1beta.DataStoreServiceClient(credentials=service_account.Credentials.from_service_account_file(VertexService.SERVICE_ACCOUNT_PATH))

            # The full resource name of the collection
            parent = client.collection_path(
                project=VertexService.PROJECT_ID,
                location=VertexService.LOCATION,
                collection="default_collection",
            )

            # Create chunking config
            chunking_config = discoveryengine_v1beta.DocumentProcessingConfig.ChunkingConfig(layout_based_chunking_config=discoveryengine_v1beta.DocumentProcessingConfig.ChunkingConfig.LayoutBasedChunkingConfig(chunk_size=500, include_ancestor_headings=True))

            # Create document processing config
            doc_processing_config = discoveryengine_v1beta.DocumentProcessingConfig(chunking_config=chunking_config)

            data_store = discoveryengine_v1beta.DataStore(display_name=f"property_information_{data_store_id}", industry_vertical=discoveryengine_v1beta.IndustryVertical.GENERIC, solution_types=[discoveryengine_v1beta.SolutionType.SOLUTION_TYPE_SEARCH], content_config=discoveryengine_v1beta.DataStore.ContentConfig.CONTENT_REQUIRED, document_processing_config=doc_processing_config)

            request = discoveryengine_v1beta.CreateDataStoreRequest(
                parent=parent,
                data_store_id=data_store_id,
                data_store=data_store,
            )

            # Make the request
            operation = client.create_data_store(request=request)
            print(f"Waiting for operation to complete: {operation.operation.name}")
            result = operation.result()

            # Get metadata after operation is complete
            metadata = discoveryengine_v1beta.CreateDataStoreMetadata(operation.metadata)
            print(f"Created data store: {result.name}")
            print(f"Metadata: {metadata}")

            return result.name

        except Exception as e:
            print(f"Error creating data store: {e}")
            raise

    @staticmethod
    def test_create_data_store():
        """Test creating a new data store"""
        try:
            # Create a client
            client = discoveryengine_v1beta.DataStoreServiceClient(credentials=service_account.Credentials.from_service_account_file(VertexService.SERVICE_ACCOUNT_PATH))

            # The full resource name of the collection
            parent = client.collection_path(
                project=VertexService.PROJECT_ID,
                location=VertexService.LOCATION,
                collection="default_collection",
            )

            # Create chunking config
            chunking_config = discoveryengine_v1beta.DocumentProcessingConfig.ChunkingConfig(layout_based_chunking_config=discoveryengine_v1beta.DocumentProcessingConfig.ChunkingConfig.LayoutBasedChunkingConfig(chunk_size=500, include_ancestor_headings=True))

            # Create document processing config
            doc_processing_config = discoveryengine_v1beta.DocumentProcessingConfig(chunking_config=chunking_config)

            data_store = discoveryengine_v1beta.DataStore(display_name="My Test Data Store2", industry_vertical=discoveryengine_v1beta.IndustryVertical.GENERIC, solution_types=[discoveryengine_v1beta.SolutionType.SOLUTION_TYPE_SEARCH], content_config=discoveryengine_v1beta.DataStore.ContentConfig.CONTENT_REQUIRED, document_processing_config=doc_processing_config)

            request = discoveryengine_v1beta.CreateDataStoreRequest(
                parent=parent,
                data_store_id="amastay-ds-test2",
                data_store=data_store,
            )

            # Make the request
            operation = client.create_data_store(request=request)
            print(f"Waiting for operation to complete: {operation.operation.name}")
            result = operation.result()

            # Get metadata after operation is complete
            metadata = discoveryengine_v1beta.CreateDataStoreMetadata(operation.metadata)
            print(f"Created data store: {result.name}")
            print(f"Metadata: {metadata}")

            return result

        except Exception as e:
            print(f"Error creating data store: {e}")
            raise

    @staticmethod
    async def import_documents(Property: property) -> bool:
        """Import documents from GCS into a data store"""
        try:
            client = discoveryengine_v1beta.DocumentServiceClient(credentials=service_account.Credentials.from_service_account_file(VertexService.SERVICE_ACCOUNT_PATH))

            # Get the full resource name of the data store
            parent = client.data_store_path(
                project=VertexService.PROJECT_ID,
                location=VertexService.LOCATION,
                data_store=data_store_id,
            )

            # Create import request
            request = discoveryengine_v1beta.ImportDocumentsRequest(parent=parent, gcs_source=discoveryengine_v1beta.GcsSource(input_uris=[gcs_uri], data_schema="content"), reconciliation_mode=discoveryengine_v1beta.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL)

            # Start the import operation
            operation = client.import_documents(request=request)
            print(f"Waiting for import operation to complete: {operation.operation.name}")

            # Wait for operation to complete
            result = operation.result()

            print(f"Import completed: {result}")
            return True

        except Exception as e:
            print(f"Error importing documents: {e}")
            raise

    @staticmethod
    async def create_document(data_store_id: str, document_id: str, content: str) -> bool:
        """Create a single document in the data store"""
        try:
            client = discoveryengine_v1beta.DocumentServiceClient(credentials=service_account.Credentials.from_service_account_file(VertexService.SERVICE_ACCOUNT_PATH))

            parent = client.data_store_path(
                project=VertexService.PROJECT_ID,
                location=VertexService.LOCATION,
                data_store=data_store_id,
            )

            # Create document
            document = discoveryengine_v1beta.Document(id=document_id, content=content, content_type="text/plain")

            request = discoveryengine_v1beta.CreateDocumentRequest(parent=parent, document=document, document_id=document_id)

            response = client.create_document(request=request)
            print(f"Created document: {response.name}")
            return True

        except Exception as e:
            print(f"Error creating document: {e}")
            raise


if __name__ == "__main__":
    # Test creating a data store
    VertexService.test_create_data_store()

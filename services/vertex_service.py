import logging
import os
from google.cloud import discoveryengine_v1beta
from google.cloud import storage
from google.api_core.client_options import ClientOptions
import asyncio
from typing import Optional, List, Tuple
from google.oauth2 import service_account
import json
from datetime import datetime
from google.api_core import exceptions

from models.property_model import Property


class VertexService:
    """Service for managing Vertex AI Search operations"""

    PROJECT_ID = "amastay"
    LOCATION = "global"
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "amastay_service_account.json")
    MAX_RETRIES = 3
    RETRY_DELAY = 2
    BUCKET_NAME = "amastay_property_data_text"

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
    async def create_data_store(property_id: str) -> str:
        """Create a data store for a property if it doesn't exist"""
        try:
            data_store_id = f"property_information_{property_id}"
            client = discoveryengine_v1beta.DataStoreServiceClient(credentials=service_account.Credentials.from_service_account_file(VertexService.SERVICE_ACCOUNT_PATH))

            # Check if data store exists
            try:
                parent = client.data_store_path(project=VertexService.PROJECT_ID, location=VertexService.LOCATION, data_store=data_store_id)
                existing_store = client.get_data_store(name=parent)
                logging.info(f"Data store already exists for property {property_id}")
                return data_store_id

            except exceptions.NotFound:
                # Data store doesn't exist, create it
                logging.info(f"Creating new data store for property {property_id}")
                parent = f"projects/{VertexService.PROJECT_ID}/locations/{VertexService.LOCATION}/collections/default_collection"

                # Create chunking config
                chunking_config = discoveryengine_v1beta.DocumentProcessingConfig.ChunkingConfig(layout_based_chunking_config=discoveryengine_v1beta.DocumentProcessingConfig.ChunkingConfig.LayoutBasedChunkingConfig(chunk_size=500, include_ancestor_headings=True))

                # Create document processing config
                doc_processing_config = discoveryengine_v1beta.DocumentProcessingConfig(chunking_config=chunking_config)

                # Create data store config with both chunking and chat
                data_store = discoveryengine_v1beta.DataStore(display_name=f"Property Information - {property_id}", industry_vertical=discoveryengine_v1beta.IndustryVertical.GENERIC, solution_types=[discoveryengine_v1beta.SolutionType.SOLUTION_TYPE_GENERATIVE_CHAT], content_config=discoveryengine_v1beta.DataStore.ContentConfig.CONTENT_REQUIRED, document_processing_config=doc_processing_config)

                request = discoveryengine_v1beta.CreateDataStoreRequest(parent=parent, data_store_id=data_store_id, data_store=data_store)

                operation = client.create_data_store(request=request)
                result = operation.result()  # Wait for operation to complete
                logging.info(f"Successfully created data store: {result.name}")
                return data_store_id

        except exceptions.AlreadyExists:
            # Handle race condition where store was created between our check and create
            logging.info(f"Data store was created concurrently for property {property_id}")
            return data_store_id
        except Exception as e:
            logging.error(f"Error creating data store for property {property_id}: {e}")
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

            data_store = discoveryengine_v1beta.DataStore(display_name="My Test Data Store2", industry_vertical=discoveryengine_v1beta.IndustryVertical.GENERIC, solution_types=[discoveryengine_v1beta.SolutionType.SOLUTION_TYPE_GENERATIVE_CHAT], content_config=discoveryengine_v1beta.DataStore.ContentConfig.CONTENT_REQUIRED, document_processing_config=doc_processing_config)

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
    async def import_documents(property: Property) -> bool:
        """Import documents from GCS into a data store"""
        try:
            client = discoveryengine_v1beta.DocumentServiceClient(credentials=service_account.Credentials.from_service_account_file(VertexService.SERVICE_ACCOUNT_PATH))
            data_store_id = f"property_information_{property.id}"
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
    async def create_document(data_store_id: str, document_id: str, content: dict):
        """Create a document in a specific data store."""
        try:
            client = discoveryengine_v1beta.DocumentServiceClient(credentials=service_account.Credentials.from_service_account_file(VertexService.SERVICE_ACCOUNT_PATH))

            parent = client.data_store_path(
                project=VertexService.PROJECT_ID,
                location=VertexService.LOCATION,
                data_store=data_store_id,
            )

            # Create document
            document = discoveryengine_v1beta.Document(id=document_id, content=content, content_type="application/json")

            request = discoveryengine_v1beta.CreateDocumentRequest(parent=parent, document=document, document_id=document_id)

            response = client.create_document(request=request)
            logging.info(f"Created document: {response.name}")

        except Exception as e:
            logging.error(f"Error creating document: {e}")
            raise

    @staticmethod
    async def index_property(property_id: str, property_data: dict, files: List[Tuple[str, str]], data_store_id: str):
        """Index property data and files in vertex search."""
        try:
            logging.info(f"Starting to index property {property_id} in data store {data_store_id}")
            logging.info(f"Property data keys: {property_data.keys()}")
            logging.info(f"Number of files to index: {len(files)}")

            # Prepare document for indexing
            document = {
                "id": property_id,
                "content": {"title": property_data.get("title", ""), "description": property_data.get("description", ""), "amenities": property_data.get("amenities", []), "location": property_data.get("location", {}), "files": files},
                "metadata": {"type": "property", "created_at": datetime.now().isoformat(), "source": property_data.get("source", ""), "url": property_data.get("url", "")},
            }
            logging.info(f"Prepared document for indexing: {json.dumps(document, indent=2)}")

            # Create document in the specific data store
            logging.info("Creating document in data store")
            await VertexService.create_document(data_store_id, property_id, document)
            logging.info("Successfully created document")

            # Import files to the data store
            if files:
                logging.info(f"Starting file import for {len(files)} files")
                await VertexService.import_files_to_data_store(data_store_id, files)
                logging.info("Successfully imported all files")
            else:
                logging.info("No files to import")

            logging.info(f"Successfully completed indexing for property {property_id}")

        except Exception as e:
            logging.error(f"Failed to index property in vertex: {e}")
            raise

    @staticmethod
    async def import_files_to_data_store(data_store_id: str, files: List[Tuple[str, str]]):
        """Import files into a specific data store."""
        try:
            logging.info(f"Starting file import to data store {data_store_id}")
            client = discoveryengine_v1beta.DocumentServiceClient(credentials=service_account.Credentials.from_service_account_file(VertexService.SERVICE_ACCOUNT_PATH))

            parent = client.data_store_path(
                project=VertexService.PROJECT_ID,
                location=VertexService.LOCATION,
                data_store=data_store_id,
            )
            logging.info(f"Using parent path: {parent}")

            # Convert local paths to GCS URIs and maintain content types
            gcs_files = [{"uri": f"gs://{VertexService.BUCKET_NAME}/{file_path}", "content_type": content_type} for file_path, content_type in files]
            logging.info(f"Prepared GCS files: {json.dumps(gcs_files, indent=2)}")

            # Create import request for each file with its content type
            for idx, file_info in enumerate(gcs_files, 1):
                logging.info(f"Processing file {idx}/{len(gcs_files)}: {file_info['uri']}")
                request = discoveryengine_v1beta.ImportDocumentsRequest(
                    parent=parent, gcs_source=discoveryengine_v1beta.GcsSource(input_uris=[file_info["uri"]], data_schema="content"), document_option=discoveryengine_v1beta.ImportDocumentsRequest.DocumentOption(content_type=file_info["content_type"]), reconciliation_mode=discoveryengine_v1beta.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL
                )

                # Start the import operation
                operation = client.import_documents(request=request)
                logging.info(f"Started import operation: {operation.operation.name}")

                # Wait for operation to complete
                result = operation.result()
                logging.info(f"Import completed for file {idx}: {result}")

            logging.info("Successfully completed all file imports")

        except Exception as e:
            logging.error(f"Error importing files to data store: {e}")
            raise


if __name__ == "__main__":
    # Test creating a data store
    VertexService.test_create_data_store()

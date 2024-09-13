import logging
from utils import supabase
import io
import tempfile
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create an in-memory file-like object with 'Test content'
file_content = io.BytesIO(b'Test content')

try:
    # Create a temporary file and write the in-memory content to it
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_content.getvalue())  # Write in-memory content to the file
        temp_file.seek(0)  # Move the cursor back to the beginning of the file
        temp_file_path = temp_file.name

    # Generate a unique filename to avoid collisions
    filename = 'test_file_' + next(tempfile._get_candidate_names()) + '.txt'

    # Test Supabase storage upload by uploading the temporary file
    logging.info(f"Uploading file: {filename}")
    response = supabase.storage.from_('properties').upload(filename, temp_file_path)

    # Check upload response
    if response:
        logging.info(f"File '{filename}' uploaded successfully.")
        print(f"File '{filename}' uploaded successfully.")
        
        # Now test the deletion process
        delete_response = supabase.storage.from_('properties').remove([filename])

        if delete_response:
            logging.info(f"File '{filename}' deleted successfully.")
            print(f"File '{filename}' deleted successfully.")
        else:
            logging.error(f"Failed to delete file '{filename}'.")
            print(f"Failed to delete file '{filename}'.")

    else:
        logging.error(f"Failed to upload file '{filename}'.")
        print(f"Failed to upload file '{filename}'.")

except Exception as e:
    logging.error(f"An error occurred during the upload or deletion: {str(e)}")
    print(f"An error occurred during the upload or deletion: {str(e)}")

finally:
    # Cleanup: Remove the temporary local file
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)
        logging.info(f"Temporary file '{temp_file_path}' deleted.")
        print(f"Temporary file '{temp_file_path}' deleted.")

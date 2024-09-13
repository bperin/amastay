# import logging
# from utils import supabase
# import io
# import tempfile
# import os

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# # Create an in-memory file-like object with 'Test content'
# file_content = io.BytesIO(b'Test content')

# try:
#     # Create a temporary file and write the in-memory content to it
#     with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#         temp_file.write(file_content.getvalue())  # Write in-memory content to the file
#         temp_file.seek(0)  # Move the cursor back to the beginning of the file
#         temp_file_path = temp_file.name

#     # Test Supabase storage upload by uploading the temporary file
#     response = supabase.storage.from_('properties').upload('test.txt', temp_file_path)

#     # Check upload response
#     if response:
#         logging.info("Test document uploaded successfully.")
#         print("Test document uploaded successfully.")
#     else:
#         logging.error("Failed to upload test document.")
#         print("Failed to upload test document.")
        
# except Exception as e:
#     logging.error(f"An error occurred during the upload: {str(e)}")
#     print(f"An error occurred during the upload: {str(e)}")

# finally:
#     # Cleanup: Remove the temporary file
#     if os.path.exists(temp_file_path):
#         os.remove(temp_file_path)
#         logging.info("Temporary file deleted.")
#         print("Temporary file deleted.")

import logging
import os
from datetime import datetime

import azure.functions as func
import azure.durable_functions as df
from azure.storage.blob import BlobServiceClient
from PIL import Image
import io
import pyodbc

# Create Durable Functions app instance
my_app = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# Initialize BlobServiceClient with connection string from environment
blob_service_client = BlobServiceClient.from_connection_string(os.environ["AzureWebJobsStorage"])

# Blob trigger function to start orchestration when a blob is uploaded to 'images-input' container
@my_app.blob_trigger(arg_name="myblob", path="images-input/{name}", connection="AzureWebJobsStorage")
@my_app.durable_client_input(client_name="client")
async def blob_trigger(myblob: func.InputStream, client):
    logging.info(f"Blob trigger processed blob: Name={myblob.name}, Size={myblob.length} bytes")
    
    # Extract blob name (filename only)
    blob_name = myblob.name.split("/")[-1]
    
    # Start the orchestration passing the blob name as input
    await client.start_new("orchestrator", client_input=blob_name)
    logging.info(f"Started orchestration for blob: {blob_name}")

# Orchestrator function coordinates metadata extraction and storage
@my_app.orchestration_trigger(context_name="context")
def orchestrator(context: df.DurableOrchestrationContext):
    blob_name = context.get_input()

    retry_options = df.RetryOptions(first_retry_interval_in_milliseconds=5000, max_number_of_attempts=3)

    # Call extract_metadata activity with retry
    metadata = yield context.call_activity_with_retry("extract_metadata", retry_options, blob_name)
    
    # Call store_metadata activity with retry
    yield context.call_activity_with_retry("store_metadata", retry_options, metadata)

    return f"Metadata processed and stored for {blob_name}"

# Activity function: Extract image metadata from blob
@my_app.activity_trigger(input_name='blob_name')
def extract_metadata(blob_name):
    logging.info(f"Extracting metadata for blob: {blob_name}")
    
    container_client = blob_service_client.get_container_client("images-input")
    blob_client = container_client.get_blob_client(blob_name)
    
    # Download blob content
    blob_bytes = blob_client.download_blob().readall()

    with Image.open(io.BytesIO(blob_bytes)) as img:
        metadata = {
            "FileName": blob_name,
            "FileSizeKB": round(len(blob_bytes) / 1024, 2),
            "Width": img.width,
            "Height": img.height,
            "Format": img.format
        }
    
    logging.info(f"Extracted metadata: {metadata}")
    return metadata

# Activity function: Store extracted metadata into Azure SQL Database
@my_app.activity_trigger(input_name='metadata')
def store_metadata(metadata):
    logging.info(f"Storing metadata in SQL Database: {metadata}")

    # Use environment variables for sensitive info - set these in your local.settings.json or app settings
    conn_str = (
        "Driver={ODBC Driver 18 for SQL Server};"
        "Server=tcp:" + os.environ.get("SQL_SERVER", "serverlesstest1.database.windows.net") + ",1433;"
        "Database=" + os.environ.get("SQL_DATABASE", "serverless") + ";"
        "Uid=" + os.environ.get("SQL_USER", "adminuser") + ";"
        "Pwd=" + os.environ.get("SQL_PASSWORD", "YourPasswordHere") + ";"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO ImageMetadata (FileName, FileSizeKB, Width, Height, Format)
            VALUES (?, ?, ?, ?, ?)
        """
        cursor.execute(insert_query, metadata["FileName"], metadata["FileSizeKB"], metadata["Width"], metadata["Height"], metadata["Format"])
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Metadata stored successfully.")
    except Exception as e:
        logging.error(f"Failed to store metadata: {e}")
        raise

    return "Metadata stored successfully."

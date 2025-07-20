import logging
import azure.functions as func
import azure.durable_functions as df

app = func.FunctionApp()

@app.function_name("BlobTriggerClient")
@app.blob_trigger(arg_name="blob", path="images-input/{name}", connection="AzureWebJobsStorage")
async def blob_trigger_client(blob: func.InputStream, starter: str):
    client = df.DurableOrchestrationClient(starter)
    logging.info(f"Blob trigger processed blob: {blob.name}, size: {blob.length} bytes")

    instance_id = await client.start_new("OrchestratorFunction", None, blob.name)
    logging.info(f"Started orchestration with ID = '{instance_id}'.")

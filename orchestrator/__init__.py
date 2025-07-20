import azure.durable_functions as df

async def main(context: df.DurableOrchestrationContext):
    blob_name = context.get_input()
    metadata = await context.call_activity("ExtractMetadataFunction", blob_name)
    await context.call_activity("StoreMetadataFunction", metadata)
    return "Processing complete."

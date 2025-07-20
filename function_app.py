import azure.durable_functions as df
import azure.functions as func

app = func.FunctionApp()

# Orchestrator function
@app.function_name("OrchestratorFunction")
@df.Orchestrator.create
async def orchestrator_function(context: df.DurableOrchestrationContext):
    result1 = await context.call_activity("ActivityFunction", "Seattle")
    result2 = await context.call_activity("ActivityFunction", "Tokyo")
    result3 = await context.call_activity("ActivityFunction", "London")
    return [result1, result2, result3]

# Activity function
@app.function_name("ActivityFunction")
@df.ActivityTrigger(input_name="city")
def activity_function(city: str):
    return f"Hello {city}!"

# HTTP trigger to start orchestrator
@app.function_name("OrchestratorFunction_HttpStart")
@app.route(route="orchestrators/{functionName}")
@app.durable_client_input(client_name="client")
async def http_start(req: func.HttpRequest, client: df.DurableOrchestrationClient):
    function_name = req.route_params.get('functionName')
    instance_id = await client.start_new(function_name, None, None)
    return client.create_check_status_response(req, instance_id)

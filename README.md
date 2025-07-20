# Image Metadata Function Lab

This repository contains an Azure Functions project implementing Durable Functions with Python. The goal is to create an orchestrator, activity functions, and an HTTP starter to demonstrate Durable Functions workflows.

---

## Current Status

### Why the function is **not working** currently

While trying to run the Azure Durable Functions locally, the project encounters the following errors:

- **`AttributeError: 'FunctionApp' object has no attribute 'durable_orchestration_trigger'`**
- **`AttributeError: module 'azure.durable_functions' has no attribute 'activity_trigger'`**
- **ModuleNotFoundError for `azure.durable_functions`**
- Other indexing errors from Azure Functions Core Tools during `func start`.

### Root Causes and Notes

1. **Azure Functions Python SDK version mismatch**  
   The `azure-functions` and `azure-functions-durable` Python packages, as well as Azure Functions Core Tools, must be compatible. Some decorators like `durable_orchestration_trigger` and `activity_trigger` are not present in the versions installed or the usage pattern has changed in the latest SDKs.

2. **Incorrect or outdated usage of Durable Functions decorators**  
   The Azure Durable Functions Python programming model has evolved.  
   For example, recent versions use decorators like `@df.Orchestrator.create` instead of `@app.durable_orchestration_trigger`.

3. **Environment issues**  
   The Python virtual environment may lack the required packages or the Azure Functions Core Tools version might not fully support the current SDK version.

4. **Local runtime conflicts**  
   Ports conflicts or caching issues might cause the Functions runtime to fail indexing.

---

## What Was Tried

- Installing and upgrading `azure-functions` and `azure-functions-durable` packages.
- Changing the function decorators according to official samples.
- Running the function app with different ports.
- Ensuring the virtual environment is activated.
- Confirming the `requirements.txt` includes all necessary dependencies.

---
<img width="1470" height="956" alt="Screenshot 2025-07-19 at 9 02 13 PM" src="https://github.com/user-attachments/assets/8127118c-8baf-4bd1-bc5d-1be730815d1e" />

<img width="1470" height="956" alt="Screenshot 2025-07-19 at 9 02 31 PM" src="https://github.com/user-attachments/assets/9689e354-9e33-44cf-bcbb-a7cf79f9d93e" />

<img width="1470" height="956" alt="Screenshot 2025-07-19 at 9 02 23 PM" src="https://github.com/user-attachments/assets/f4397442-5771-47a0-aebf-7048ff8d5595" />




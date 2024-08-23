import boto3

# Initialize the SageMaker client
sagemaker_client = boto3.client('sagemaker', region_name='us-east-1')

# Step 1: List all endpoints
response = sagemaker_client.list_endpoints()

# Step 2: Iterate through each endpoint and delete it
for endpoint in response['Endpoints']:
    endpoint_name = endpoint['EndpointName']
    print(f"Deleting endpoint: {endpoint_name}")
    sagemaker_client.delete_endpoint(EndpointName=endpoint_name)

print("All endpoints have been undeployed.")

# List all models
models = sagemaker_client.list_models()

# Iterate through each model and delete it
for model in models['Models']:
    model_name = model['ModelName']
    sagemaker_client.delete_model(ModelName=model_name)
    print(f"Deleted model: {model_name}")

# Handle pagination in case there are many models
while 'NextToken' in models:
    models = sagemaker_client.list_models(NextToken=models['NextToken'])
    for model in models['Models']:
        model_name = model['ModelName']
        sagemaker_client.delete_model(ModelName=model_name)
        print(f"Deleted model: {model_name}")

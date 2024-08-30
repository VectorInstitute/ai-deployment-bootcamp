import json
from datetime import datetime, timedelta

import boto3
import sagemaker
from botocore.config import Config
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sagemaker.predictor import Predictor

# Replace with your SageMaker endpoint name
endpoint_name = 'paraphrase-bert-en-g4dn-202408-2310-3917'
region = "us-east-1"

config = Config(
    read_timeout=300,  # Timeout for reading response
    connect_timeout=60  # Timeout for establishing connection
)

# Create a SageMaker runtime client with the custom config
client = boto3.client('sagemaker-runtime', config=config)
# Initialize the SageMaker runtime client
runtime_client = boto3.client('sagemaker-runtime', region_name='us-east-1', config=config)
endpoint_client = boto3.client('sagemaker')
# print(endpoint_client.list_endpoints())


response = endpoint_client.describe_endpoint(EndpointName=endpoint_name)
print(f"Endpoint Status: {response['EndpointStatus']}")

cloudwatch = boto3.client('cloudwatch')

response = cloudwatch.get_metric_statistics(
    Namespace='AWS/SageMaker',
    MetricName='Invocations',
    Dimensions=[
        {'Name': 'EndpointName', 'Value': endpoint_name},
    ],
    StartTime=datetime.utcnow() - timedelta(minutes=60),
    EndTime=datetime.utcnow(),
    Period=60,
    Statistics=['Sum']
)

print(f"{response=}")

for datapoint in response['Datapoints']:
    print(f"Time: {datapoint['Timestamp']}, Invocations: {datapoint['Sum']}")


try:
	role = sagemaker.get_execution_role()
except ValueError:
	iam = boto3.client('iam')
	role = iam.get_role(RoleName='sagemaker_execution_role')['Role']['Arn']
	
print(f"Role: \n{role=}")



# Example input data for model inference
input_data = {
    # Your input data goes here
    'seq_0': "The fluffy white cat curled up on the cozy armchair, napping peacefully in the warm sunlight streaming through the window.",
    'seq_1': "Snuggling comfortably in the sunlit armchair, the soft, white cat dozed off, enjoying a tranquil nap."
    
}

# Convert input data to JSON string
payload = json.dumps(input_data)

print(f"{payload=}")

# Invoke the SageMaker endpoint
response = runtime_client.invoke_endpoint(
    EndpointName=endpoint_name,
    ContentType='application/json',
    Body=payload
)

# Parse the response
result = json.loads(response['Body'].read().decode())

print("Model inference result:", result)
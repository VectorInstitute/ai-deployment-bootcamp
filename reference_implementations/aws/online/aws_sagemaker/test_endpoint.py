import json
from datetime import datetime, timedelta

import boto3
import sagemaker
from botocore.config import Config

# Replace with your SageMaker endpoint name
endpoint_name = 'paraphrase-bert-en-endpoint'
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



# "The sky is blue.","The grass is green."
# Example input data for model inference
input_data = {
    # Your input data goes here
    'seq_0': "The sky is blue.",
    'seq_1': "The name of the Feature used for RecordIdentifier , whose value uniquely identifies a record stored in the feature store."
    
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
import boto3
import json
import logging
import argparse

# Function to publish message to SQS
def publish_message_to_sqs(queue_url, message_body):
    sqs_client = boto3.client('sqs')
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body
    )
    return response['MessageId']

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Parse the ID from command line arguments
parser = argparse.ArgumentParser(description="Publish message to SQS with a given ID.")
parser.add_argument("id", type=str, help="The ID to include in the SQS message.")
args = parser.parse_args()

# SQS queue URL - TODO: Replace with your queue URL
queue_url = 'https://sqs.us-east-1.amazonaws.com/025066243062/inference_queue'

# Prepare input data
input_data = {
    "id": args.id  # Get the ID from command-line argument
}

# Convert input data to JSON string
payload = json.dumps(input_data)
message_id = publish_message_to_sqs(queue_url, payload)
logger.info(f"Message published with ID: {message_id}")

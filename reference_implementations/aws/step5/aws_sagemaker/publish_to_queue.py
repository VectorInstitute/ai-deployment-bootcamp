import boto3
import logging
import json

def publish_message_to_sqs(queue_url, message_body):
    sqs_client = boto3.client('sqs')
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body
    )
    return response['MessageId']


logger = logging.getLogger(__name__)

queue_url = 'https://sqs.us-east-1.amazonaws.com/025066243062/my_queue'
# input_data = {
#         "seq_0": "The cat chased the mouse.",
#         "seq_1": "The mouse was chased by the cat."
#     }

input_data = {
        "id": "2"
    }

# Convert input data to JSON string
payload = json.dumps(input_data)
message_id = publish_message_to_sqs(queue_url, payload)
logger.info(f"Message published with ID: {message_id}")

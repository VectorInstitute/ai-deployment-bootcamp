import boto3
import logging

def publish_message_to_sqs(queue_url, message_body):
    sqs_client = boto3.client('sqs')
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=message_body
    )
    return response['MessageId']


logger = logging.getLogger(__name__)

queue_url = 'https://sqs.us-east-1.amazonaws.com/025066243062/my_queue'
message_body = 'Hello, Lambda!'
message_id = publish_message_to_sqs(queue_url, message_body)
logger.info(f"Message published with ID: {message_id}")

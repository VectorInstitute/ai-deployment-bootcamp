import json
import logging
import os

import boto3
from aws_lambda_powertools.event_handler import (
    APIGatewayRestResolver,
    CORSConfig,
    content_types,
)
from sagemaker.feature_store.feature_group import FeatureGroup
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_sagemaker.constants import TFVARS

cors_config = CORSConfig()
app = APIGatewayRestResolver(cors=cors_config)
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

ENDPOINT_NAME = os.environ.get("ENDPOINT_NAME")

runtime_client = boto3.client("runtime.sagemaker")
fs_client = boto3.client('sagemaker-featurestore-runtime')
feature_group_name = TFVARS["feature_group_name"]
feature_group = FeatureGroup(
    name=feature_group_name)
# Run command below from your terminal to see if the enpoint works:
# aws lambda invoke --function-name bert-paraphrase-tf --payload '{"seq_0": "hello, world!", "seq_1": "goodbye, world!"}' response.json


@app.post("/predict")
def get_predictions():
    logger.info("received data input in predict rest endpoint")

    data = app.current_event.json_body
    seq_0 = data.get("seq_0")
    seq_1 = data.get("seq_1")

    input_data = {
        "seq_0": seq_0,
        "seq_1": seq_1,
    }

    # Convert input data to JSON string
    payload = json.dumps(input_data)
    logger.info(f"Payload: {payload}")
    if not data or not seq_0 or not seq_1:

        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": payload
        }

    try:
        logger.info("Calling ML Server...")
        response = runtime_client.invoke_endpoint(
            EndpointName=ENDPOINT_NAME, ContentType="application/json", Body=payload
        )

        result = json.loads(response["Body"].read().decode())
        logger.info(f"Result from ML server: {result}")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result),
        }
    except Exception as e:
        logger.info("Bad request...")
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"message": f"Unhandled exception in predict: {e}"}
            ),  
        }
    
@app.get("/predict/{id}")
def predict(id: str):
    logger.info("Received {id=}")

    record = fs_client.get_record(
        FeatureGroupName=feature_group_name,
        RecordIdentifierValueAsString=str(id)
    )
    if not record:
        logger.info(f"No matching record found for {id=}")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"message": "Error in finding record"}
            )
        }
    input_data = {
        "seq_0": record["seq_0"],
        "seq_1": record["seq_1"],
    }
    payload = json.dumps(input_data)

    try:
        logger.info("Calling ML Server...")
        response = runtime_client.invoke_endpoint(
            EndpointName=ENDPOINT_NAME, ContentType="application/json", Body=payload
        )

        result = json.loads(response["Body"].read().decode())
        logger.info(f"Result from ML server: {result}")

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result),
        }
    except Exception as e:
        logger.info("Bad request...")
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {"message": f"Unhandled exception in predict: {e}"}
            ),  
        }


def lambda_handler(event: dict, context: LambdaContext) -> dict:
    try:
        logger.info(f"In lambda handler - Event:\n {event}")
        return app.resolve(event, context)
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)

        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(
                {
                    "message": f"Unhandled exception in lambda_handler: {e} - Event: \n {event} \n Context:\n {context}"
                }
            ),
        }

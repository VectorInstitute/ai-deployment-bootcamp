import json
import logging
import os

import boto3
from aws_lambda_powertools.event_handler import APIGatewayRestResolver, CORSConfig
from aws_lambda_powertools.utilities.typing import LambdaContext

cors_config = CORSConfig()
app = APIGatewayRestResolver(cors=cors_config)
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)

ENDPOINT_NAME = os.environ.get("ENDPOINT_NAME")
FEATURE_GROUP_NAME = os.environ.get("FEATURE_GROUP_NAME")
# REGION = os.environ.get('AWS_DEFAULT_REGION')

session = boto3.session.Session()
sagemaker_runtime = boto3.client("runtime.sagemaker")
logger.info(f"boto3 session={session}, sagemaker_runtime={sagemaker_runtime}")

sagemaker_featurestore_client = session.client(
    service_name="sagemaker-featurestore-runtime", region_name=session.region_name
)


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
            "body": payload,
        }

    try:
        logger.info("Calling ML Server...")
        response = sagemaker_runtime.invoke_endpoint(
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
            "body": json.dumps({"message": f"Unhandled exception in predict: {e}"}),
        }


@app.get("/predict/<id>")
def predict(id: str):
    logger.info(f"Received {id=}")

    response = sagemaker_featurestore_client.get_record(
        FeatureGroupName=FEATURE_GROUP_NAME,
        RecordIdentifierValueAsString=str(id),
        FeatureNames=["seq_0", "seq_1"],
    )
    # This is how a response looks like:
    # response={'ResponseMetadata': {'RequestId': '09e5395b-608d-4de4-b83f-c6066025667c', 'HTTPStatusCode': 200, 'HTTPHeaders': {'x-amzn-requestid': '09e5395b-608d-4de4-b83f-c6066025667c', 'content-type': 'application/json', 'content-length': '282', 'date': 'Sat, 21 Sep 2024 19:25:22 GMT'}, 'RetryAttempts': 0}, 'Record': [{'FeatureName': 'id', 'ValueAsString': '3'}, {'FeatureName': 'seq_0', 'ValueAsString': 'The dog barked loudly.'}, {'FeatureName': 'seq_1', 'ValueAsString': 'The canine vocalized noisily.'}]}"
    if not response:
        logger.info(f"No matching record found for {id=}")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Error in finding record"}),
        }
    # We need 'Record' value:
    # 'Record': [{'FeatureName': 'id', 'ValueAsString': '3'}, {'FeatureName': 'seq_0', 'ValueAsString': 'The dog barked loudly.'}, {'FeatureName': 'seq_1', 'ValueAsString': 'The canine vocalized noisily.'}]
    record = response["Record"][
        0
    ]  # First item in returned records since we retrieved using ID
    features = [record["ValueAsString"] for _ in record]
    logger.info(f"{response=}")

    input_data = {
        "seq_0": features[0],
        "seq_1": features[1],
    }
    payload = json.dumps(input_data)

    try:
        logger.info("Calling ML Server...")
        response = sagemaker_runtime.invoke_endpoint(
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
            "body": json.dumps({"message": f"Unhandled exception in predict: {e}"}),
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

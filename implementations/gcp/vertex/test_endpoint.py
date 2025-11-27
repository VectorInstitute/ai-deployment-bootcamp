import logging
import sys

from google.api import httpbody_pb2
from google.cloud import aiplatform_v1

from constants import TFVARS, PROJECT_NUMBER

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s")

input_data_path = sys.argv[1]
endpoint = sys.argv[2] if len(sys.argv) >= 3 else TFVARS["endpoint"]

with open(input_data_path, "r") as file:
    input_data = file.read()

print(f"Sending input data to endpoint {TFVARS['endpoint']}:\n{input_data}")

prediction_client = aiplatform_v1.PredictionServiceClient(
    client_options={
        "api_endpoint": f"{TFVARS['region']}-aiplatform.googleapis.com",
    }
)

http_body = httpbody_pb2.HttpBody(data=input_data.encode("utf-8"), content_type="application/json")
request = aiplatform_v1.RawPredictRequest(
    endpoint=f"projects/{PROJECT_NUMBER}/locations/{TFVARS['region']}/endpoints/{endpoint}",
    http_body=http_body,
)

response = prediction_client.raw_predict(request)
print(f"Response:\n{response.data}")

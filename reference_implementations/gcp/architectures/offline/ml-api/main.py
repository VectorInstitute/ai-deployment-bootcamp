import base64
import json
import os
import traceback
from copy import deepcopy
from enum import Enum
from typing import Dict, List, Any

from google.api import httpbody_pb2
from google.cloud import aiplatform_v1, aiplatform, bigquery


ENDPOINT_ID = os.environ.get("ENDPOINT_ID")
MODEL_NAME = os.environ.get("MODEL_NAME")
PROJECT_ID = os.environ.get("PROJECT_ID")
PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER")
REGION = os.environ.get("REGION")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
PROJECT_PREFIX = PROJECT_ID.replace("-", "_")


def process(event, context):
    print(f"Event received: {event}")

    try:
        event_data = base64.b64decode(event["data"]).decode("utf-8")
        print(f"Decoded event data: {event_data}")
        json_data = json.loads(event_data)
        data_id = json_data["id"]

        print(f"Pulling data with id {data_id} from the feature store")

        aiplatform.init(project=PROJECT_ID, location=REGION)
        entity_type = aiplatform.featurestore.EntityType(
            featurestore_id=f"{PROJECT_PREFIX}_featurestore",
            entity_type_name="data_entity",
        )

        result_df = entity_type.read(entity_ids=[data_id])
        data = result_df.get("data_feature")[0]

        if data is None:
            print(f"[ERROR] Data with id {data_id} not found in the feature store.")
            return

        prediction_client = aiplatform_v1.PredictionServiceClient(
            client_options={
                "api_endpoint": f"{REGION}-aiplatform.googleapis.com",
            }
        )

        if MODEL_NAME not in Models.list():
            raise Exception(f"Model {MODEL_NAME} not supported! Supported models: {Models.list()}")

        input_data = Models.get_input_for_model(Models[MODEL_NAME], data)

        json_input_data = json.dumps(input_data)

        print(f"Sending input data to the endpoint id {ENDPOINT_ID}: {json_input_data}")

        http_body = httpbody_pb2.HttpBody(data=json_input_data.encode("utf-8"), content_type="application/json")
        request = aiplatform_v1.RawPredictRequest(
            endpoint=f"projects/{PROJECT_NUMBER}/locations/{REGION}/endpoints/{ENDPOINT_ID}",
            http_body=http_body,
        )
        response = prediction_client.raw_predict(request)

        prediction = response.data.decode("utf-8")
        print(f"Prediction: {prediction}")

        bq_client = bigquery.Client()
        predictions_table = bq_client.get_table(f"{PROJECT_ID}.{PROJECT_PREFIX}_database.predictions_table")

        last_id_query = bq_client.query(f"SELECT max(id) as max_id from {predictions_table}")
        last_id = None
        for lid in last_id_query.result():
            last_id = lid.get("max_id", 0)

        last_id = last_id if last_id is not None else 0

        prediction_data = {"id": last_id + 1, "data_id": data_id, "prediction": prediction}
        errors = bq_client.insert_rows_json(predictions_table, [prediction_data])

        if errors is not None and len(errors) > 0:
            print(f"[ERROR] Error saving prediction to table: {errors}")
            return

        print(f"Prediction added to the DB: {prediction_data}")

    except Exception:
        print(f"[ERROR] {traceback.format_exc()}")


class Models(Enum):
    LLAMA_3_1 = "llama3.1"
    BART_MNLI_LARGE = "bart_mnli_large"

    @classmethod
    def list(cls) -> List[str]:
        return [model.value for model in Models]

    @classmethod
    def get_input_for_model(cls, model: "Model", input: str) -> Dict[str, Any]:
        if model == Models.LLAMA_3_1:
            input_dict = deepcopy(LLAMA_3_1_INPUT_TEMPLATE)
            input_dict["prompt"] = input
            return input_dict

        if model == Models.BART_MNLI_LARGE:
            input_dict = deepcopy(BART_MNLI_INPUT_TEMPLATE)
            input_dict["sequences"] = input
            return input_dict

        raise Exception(f"Model{model.value} not supported!")



LLAMA_3_1_INPUT_TEMPLATE = {
    "prompt": None,
    "max_tokens": 50,
    "temperature": 1.0,
    "top_p": 1.0,
    "top_k": 1
}

BART_MNLI_INPUT_TEMPLATE = {
    "sequences": None,
    "candidate_labels": ["mobile", "website", "billing", "account access"]
}

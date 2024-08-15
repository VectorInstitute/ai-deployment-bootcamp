import json
import os
from contextlib import asynccontextmanager
from copy import deepcopy
from enum import Enum
from typing import Dict, List, Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from google.api import httpbody_pb2
from google.cloud import aiplatform_v1, aiplatform


ENDPOINT_ID = os.getenv("ENDPOINT_ID")
MODEL_NAME = os.getenv("MODEL_NAME")
ZONE = os.getenv("ZONE")
REGION = f"{ZONE.split('-')[0]}-{ZONE.split('-')[1]}"
PROJECT_ID = os.getenv("PROJECT_ID")
PROJECT_NUMBER = os.getenv("PROJECT_NUMBER")
ENV = os.getenv("ENV")
PROJECT_PREFIX = PROJECT_ID.replace("-", "_")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """Set up function for app startup and shutdown."""
    aiplatform.init(project=PROJECT_ID, location=REGION)
    app.entity_type = aiplatform.featurestore.EntityType(
        featurestore_id=f"{PROJECT_PREFIX}_{ENV}_featurestore",
        entity_type_name="data_entity",
    )
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/predict/{data_id}")
async def predict(data_id: str):
    # fetch data
    result_df = app.entity_type.read(entity_ids=[data_id])
    data = result_df.get("data_feature")[0]

    if data is None:
        return JSONResponse(content={"error": f"Data with id {data_id} not found."}, status_code=400)

    # make prediction
    prediction_client = aiplatform_v1.PredictionServiceClient(
        client_options={
            "api_endpoint": f"{REGION}-aiplatform.googleapis.com",
        }
    )

    input_data = Models.get_input_for_model_name(MODEL_NAME, data)
    json_data = json.dumps(input_data)

    http_body = httpbody_pb2.HttpBody(data=json_data.encode("utf-8"), content_type="application/json")
    request = aiplatform_v1.RawPredictRequest(
        endpoint=f"projects/{PROJECT_NUMBER}/locations/{REGION}/endpoints/{ENDPOINT_ID}",
        http_body=http_body,
    )
    response = prediction_client.raw_predict(request)

    return {"data": data, "prediction": json.loads(response.data)}


class Models(Enum):
    LLAMA_3_1 = "llama3.1"
    BART_LARGE_MNLI = "bart-large-mnli"

    @classmethod
    def list(cls) -> List[str]:
        return [model.value for model in Models]

    @classmethod
    def get_input_for_model_name(cls, model_name: str, input: str) -> Dict[str, Any]:
        if model_name == Models.LLAMA_3_1.value:
            input_dict = deepcopy(LLAMA_3_1_INPUT_TEMPLATE)
            input_dict["prompt"] = input
            return input_dict

        if model_name == Models.BART_LARGE_MNLI.value:
            input_dict = deepcopy(BART_MNLI_INPUT_TEMPLATE)
            input_dict["sequences"] = input
            return input_dict

        raise Exception(f"Model {model_name} not supported! Supported models: {Models.list()}")


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

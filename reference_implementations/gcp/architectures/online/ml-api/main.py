import json
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from google.api import httpbody_pb2
from google.cloud import aiplatform_v1, aiplatform
from vertexai.resources.preview import FeatureView

from .models import LlamaTask, Models


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
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/predict/{data_id}")
async def predict(data_id: str, task: LlamaTask = LlamaTask.GENERATION):
    # fetch data
    features = FeatureView(
        name="featureview",
        feature_online_store_id=f"{PROJECT_PREFIX}_{ENV}_featurestore",
    ).read(key=[data_id]).to_dict()

    data = None
    for feature in features["features"]:
        if feature["name"] == "data_feature":
            data = feature["value"]["string_value"]

    if data is None:
        return JSONResponse(content={"error": f"Data with id {data_id} not found."}, status_code=400)

    # make prediction
    prediction_client = aiplatform_v1.PredictionServiceClient(
        client_options={
            "api_endpoint": f"{REGION}-aiplatform.googleapis.com",
        }
    )

    input_data = Models.get_input_for_model_name(MODEL_NAME, data, task)
    json_data = json.dumps(input_data)

    http_body = httpbody_pb2.HttpBody(data=json_data.encode("utf-8"), content_type="application/json")
    request = aiplatform_v1.RawPredictRequest(
        endpoint=f"projects/{PROJECT_NUMBER}/locations/{REGION}/endpoints/{ENDPOINT_ID}",
        http_body=http_body,
    )
    response = prediction_client.raw_predict(request)

    return {"data": data, "prediction": json.loads(response.data)}

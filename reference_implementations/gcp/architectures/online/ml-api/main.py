import json
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from google.api import httpbody_pb2
from google.cloud import aiplatform_v1, aiplatform


ENDPOINT_ID = os.getenv("ENDPOINT_ID")
ZONE = os.getenv("ZONE")
REGION = f"{ZONE.split('-')[0]}-{ZONE.split('-')[1]}"
PROJECT_ID = os.getenv("PROJECT_ID")
PROJECT_NUMBER = os.getenv("PROJECT_NUMBER")
PROJECT_PREFIX = PROJECT_ID.replace("-", "_")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """Set up function for app startup and shutdown."""
    aiplatform.init(project=PROJECT_ID, location=REGION)
    app.entity_type = aiplatform.featurestore.EntityType(
        featurestore_id="featurestore",
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

    input_data = {
        "sequences": data,
        "candidate_labels": ["mobile", "website", "billing", "account access"],
    }

    json_data = json.dumps(input_data)

    http_body = httpbody_pb2.HttpBody(data=json_data.encode("utf-8"), content_type="application/json")
    request = aiplatform_v1.RawPredictRequest(
        endpoint=f"projects/{PROJECT_NUMBER}/locations/{REGION}/endpoints/{ENDPOINT_ID}",
        http_body=http_body,
    )
    response = prediction_client.raw_predict(request)

    return {"data": data, "prediction": json.loads(response.data)}

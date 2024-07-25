import json
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from google.api import httpbody_pb2
from google.cloud import aiplatform_v1, bigquery


ENDPOINT_ID = os.getenv("ENDPOINT_ID")
ZONE = os.getenv("ZONE")
REGION = f"{ZONE.split('-')[0]}-{ZONE.split('-')[1]}"
PROJECT_ID = os.getenv("PROJECT_ID")
PROJECT_NUMBER = os.getenv("PROJECT_NUMBER")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """Set up function for app startup and shutdown."""
    app.bq_client = bigquery.Client()
    app.feature_store_table = app.bq_client.get_table(f"{PROJECT_ID}.feature_store_dataset.feature_store_table")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/predict/{data_id}")
async def predict(data_id: str):
    # fetch data
    query = app.bq_client.query(f"SELECT * from {app.feature_store_table} where feature_id = '{data_id}'")
    results = query.result()
    results_list = [r for r in results] if results is not None else []

    if len(results_list) == 0:
        return JSONResponse(content={"error": f"Data with id {data_id} not found."}, status_code=400)

    data = results_list[0]

    # make prediction
    prediction_client = aiplatform_v1.PredictionServiceClient(
        client_options={
            "api_endpoint": f"{REGION}-aiplatform.googleapis.com",
        }
    )

    input_data = {
        "sequences": data.get("feature_data"),
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

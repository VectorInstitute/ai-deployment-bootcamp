import json
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from google.api import httpbody_pb2
from google.cloud import aiplatform_v1

from db.config import get_engine
from db.entities import Base, Data

ENDPOINT_ID = "6238862072466112512"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    """Set up function for app startup and shutdown."""
    app.db_engine = get_engine()

    Base.metadata.create_all(app.db_engine)

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/predict/{data_id}")
async def predict(data_id: int):
    with Session(app.db_engine) as session:
        data_obj = session.query(Data).get(data_id)

    if data_obj is None:
        return JSONResponse(content={"error": f"Data with id {data_id} not found."}, status_code=400)

    prediction_client = aiplatform_v1.PredictionServiceClient(
        client_options={
            "api_endpoint": "us-west2-aiplatform.googleapis.com",
        }
    )

    input_data = {
        "sequences": data_obj.data,
        "candidate_labels": ["mobile", "website", "billing", "account access"],
    }

    json_data = json.dumps(input_data)

    http_body = httpbody_pb2.HttpBody(data=json_data.encode("utf-8"), content_type="application/json")
    request = aiplatform_v1.RawPredictRequest(
        endpoint=f"projects/761003357790/locations/us-west2/endpoints/{ENDPOINT_ID}",
        http_body=http_body,
    )
    response = prediction_client.raw_predict(request)

    return {"data": data_obj, "prediction": json.loads(response.data)}


@app.get("/add_data_point/{data_point}")
async def add_data_point(data_point: str):
    with Session(app.db_engine) as session:
        data = Data(data=data_point)

        session.add_all([data])
        session.commit()

        return {"data": data.to_dict()}

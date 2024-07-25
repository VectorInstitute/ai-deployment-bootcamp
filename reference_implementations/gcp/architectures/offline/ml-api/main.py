import base64
import json
import os
import traceback

from google.api import httpbody_pb2
from google.cloud import aiplatform_v1, bigquery
from sqlalchemy.orm import Session

from db.config import get_engine
from db.entities import Base, Prediction

ENDPOINT_ID = os.environ.get("ENDPOINT_ID")
PROJECT_ID = os.environ.get("PROJECT_ID")
PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER")
REGION = os.environ.get("REGION")
DB_PASSWORD = os.environ.get("DB_PASSWORD")


def process(event, context):
    print(f"Event received: {event}")

    try:
        event_data = base64.b64decode(event["data"]).decode("utf-8")
        print(f"Decoded event data: {event_data}")
        json_data = json.loads(event_data)
        data_id = json_data["id"]

        print(f"Pulling data with id {data_id} from the feature store")

        bq_client = bigquery.Client()
        feature_store_table = bq_client.get_table(f"{PROJECT_ID}.feature_store_dataset.feature_store_table")
        query = bq_client.query(f"SELECT * from {feature_store_table} where feature_id = '{data_id}'")
        results = query.result()
        results_list = [r for r in results] if results is not None else []

        if len(results_list) == 0:
            print(f"[ERROR] Data with id {data_id} not found in the feature store.")
            return

        data = results_list[0]

        prediction_client = aiplatform_v1.PredictionServiceClient(
            client_options={
                "api_endpoint": f"{REGION}-aiplatform.googleapis.com",
            }
        )

        input_data = {
            "sequences": data.get("feature_data"),
            "candidate_labels": ["mobile", "website", "billing", "account access"],
        }

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

        db_engine = get_engine(PROJECT_ID, REGION, DB_PASSWORD)
        Base.metadata.create_all(db_engine)

        with Session(db_engine) as session:
            db_prediction = Prediction(data_id=data_id, prediction=prediction)

            session.add_all([db_prediction])
            session.commit()

            print(f"Prediction added to the DB: {db_prediction.to_dict()}")

    except Exception:
        print(f"[ERROR] {traceback.format_exc()}")

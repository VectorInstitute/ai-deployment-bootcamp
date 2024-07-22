import base64
import json
import os
import traceback

from google.api import httpbody_pb2
from google.cloud import aiplatform_v1, aiplatform
from sqlalchemy.orm import Session

from db.config import get_engine
from db.entities import Base, Prediction

ENDPOINT_ID = os.environ.get("ENDPOINT_ID")
PROJECT_ID = os.environ.get("PROJECT_ID")
PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER")
REGION = os.environ.get("REGION")


def process(event, context):
    print(f"Event received: {event}")

    try:
        event_data = base64.b64decode(event["data"]).decode("utf-8")
        print(f"Decoded event data: {event_data}")
        json_data = json.loads(event_data)
        data_id = json_data['id']

        print(f"Pulling data with id {data_id} from the feature store")

        aiplatform.init(project=PROJECT_ID, location=REGION)
        entity_type = aiplatform.featurestore.EntityType(
            featurestore_id="featurestore",
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

        input_data = {
            "sequences": data,
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

        db_engine = get_engine()
        Base.metadata.create_all(db_engine)

        with Session(db_engine) as session:
            db_prediction = Prediction(data_id=data_id, prediction=prediction)

            session.add_all([db_prediction])
            session.commit()

            print(f"Prediction added to the DB: {db_prediction.to_dict()}")

    except Exception:
        print(f"[ERROR] {traceback.format_exc()}")

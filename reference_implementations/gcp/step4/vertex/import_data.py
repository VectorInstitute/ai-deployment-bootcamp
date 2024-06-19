from datetime import datetime

from google.cloud import aiplatform
from sqlalchemy.orm import Session

from db.config import get_engine
from db.entities import Data


db_engine = get_engine()
with Session(db_engine) as session:
    data_obj = session.query(Data).get()

print(data_obj)

# aiplatform.init(project="ai-deployment-bootcamp", location="us-west2")
#
# my_entity_type = aiplatform.featurestore.EntityType(
#     featurestore_id="featurestore",
#     entity_type_name="featurestore_entitytype",
# )
#
# my_entity_type.ingest_from_gcs(
#     feature_ids=["featurestore_entitytype_feature_1"],
#     feature_time=datetime.now(),  # can be replaced by timestamp db column
#     gcs_source_uris=gcs_source_uris,
#     gcs_source_type=gcs_source_type,
# )

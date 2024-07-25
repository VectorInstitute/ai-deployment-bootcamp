from datetime import datetime

from google.cloud import bigquery
from sqlalchemy.orm import Session

from db.config import get_engine
from db.entities import Data
from constants import TFVARS


db_engine = get_engine(TFVARS["project"], TFVARS["region"], TFVARS["db_password"])
with Session(db_engine) as session:
    data_list = session.query(Data).all()

data_to_import = []
data_ids = []
for data in data_list:
    data_to_import.append({
        "feature_id": data.id,
        "feature_data": data.data,
        "feature_timestamp": datetime.now().isoformat(timespec="seconds"),
        "feature_version": "v1",
    })
    data_ids.append(str(data.id))

bq_client = bigquery.Client()
feature_store_table = bq_client.get_table(f"{TFVARS['project']}.feature_store_dataset.feature_store_table")
errors = bq_client.insert_rows_json(feature_store_table, data_to_import)

if errors is not None and len(errors) > 0:
    print(f"Error saving data to feature store: {errors}")
else:
    query = bq_client.query(f"SELECT * from {feature_store_table} where feature_id in ({str(data_ids)[1:-1]})")
    print("Saved data:")
    for r in query.result():
        print(r)

from datetime import datetime

from google.cloud import bigquery

from constants import TFVARS

project_prefix = TFVARS["project"].replace("-", "_")

bq_client = bigquery.Client()
data_table = bq_client.get_table(f"{TFVARS['project']}.{project_prefix}_database.data_table")
query = bq_client.query(f"SELECT * from {data_table}")

data_to_import = []
data_ids = []
for data_point in query.result():
    data_to_import.append({
        "feature_id": data_point.get("id"),
        "feature_data": data_point.get("data"),
        "feature_timestamp": datetime.now().isoformat(timespec="seconds"),
        "feature_version": "v1",
    })
    data_ids.append(str(data_point.get("id")))

feature_store_table = bq_client.get_table(f"{TFVARS['project']}.{project_prefix}_feature_store.feature_store_table")
errors = bq_client.insert_rows_json(feature_store_table, data_to_import)

if errors is not None and len(errors) > 0:
    print(f"Error saving data to feature store: {errors}")
else:
    query = bq_client.query(f"SELECT * from {feature_store_table} where feature_id in ({str(data_ids)[1:-1]})")
    print("Saved data:")
    for r in query.result():
        print(r)

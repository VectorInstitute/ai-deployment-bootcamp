from datetime import datetime

from google.cloud import bigquery

from constants import TFVARS

project_prefix = TFVARS["project"].replace("-", "_")

bq_client = bigquery.Client()
data_table = bq_client.get_table(f"{TFVARS['project']}.{project_prefix}_{TFVARS['env']}_database.data_table")
query = bq_client.query(f"SELECT * from {data_table}")

data_to_import = []
for data in query.result():
    data_id = str(data.get("id"))
    data_feature = data.get("data")
    if data_id in [data["entity_id"] for data in data_to_import]:
        print(f"Skipping duplicated data id {data_id}. Data: {data_feature} ")
        continue

    data_to_import.append({"entity_id": data_id, "data_feature": data_feature, "feature_timestamp": datetime.now().isoformat()})

featurestore_table = bq_client.get_table(
    f"{TFVARS['project']}.{project_prefix}_{TFVARS['env']}_featurestore_dataset.featurestore_table"
)

errors = bq_client.insert_rows_json(featurestore_table, data_to_import)
if errors is not None and len(errors) > 0:
    print(f"Error saving data to table: {errors}")
else:
    print(f"Data points added.")

print("IMPORTANT: Please check the featureview details for information about data sync into the feature store.")

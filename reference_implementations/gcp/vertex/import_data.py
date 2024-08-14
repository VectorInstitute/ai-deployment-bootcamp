import time

import pandas as pd
from google.cloud import aiplatform, bigquery

from constants import TFVARS

project_prefix = TFVARS["project"].replace("-", "_")

bq_client = bigquery.Client()
data_table = bq_client.get_table(f"{TFVARS['project']}.{project_prefix}_{TFVARS['env']}_database.data_table")
query = bq_client.query(f"SELECT * from {data_table}")

data_to_import = []
indexes = []
for data in query.result():
    data_to_import.append({"data_feature": data.get("data")})
    indexes.append(str(data.get("id")))

df_to_import = pd.DataFrame(data_to_import, index=indexes)

aiplatform.init(project=TFVARS["project"], location=TFVARS["region"])

entity_type = aiplatform.featurestore.EntityType(
    featurestore_id=f"{project_prefix}_{TFVARS['env']}_featurestore",
    entity_type_name="data_entity",
)

entity_type.preview.write_feature_values(instances=df_to_import)

print("Waiting 30s for the changes to propagate...")
time.sleep(30)

print("Saved data:")
print(entity_type.read(entity_ids=indexes))

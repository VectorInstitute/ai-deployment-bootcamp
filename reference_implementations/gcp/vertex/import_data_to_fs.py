from datetime import datetime

from google.cloud import bigquery
import pandas as pd
from constants import TFVARS


project_prefix = TFVARS["project"].replace("-", "_")

bq_client = bigquery.Client()
data_table = bq_client.get_table(f"{TFVARS['project']}.{project_prefix}_{TFVARS['env']}_database.data_table")
query = bq_client.query(f"SELECT * from {data_table}")

data_to_import = query.to_dataframe()
data_to_import["feature_timestamp"] = datetime.now().isoformat()
data_to_import["feature_timestamp"] = pd.to_datetime(data_to_import["feature_timestamp"])

featurestore_table = bq_client.get_table(
    f"{TFVARS['project']}.{project_prefix}_{TFVARS['env']}_featurestore_dataset.featurestore_table"
)
job = bq_client.load_table_from_dataframe(data_to_import, featurestore_table, 
                    job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE"))


# -------- Check for errors
if job.errors is not None and len(job.errors) > 0:
    print(f"Error saving data to table: {job.errors}")


print("IMPORTANT: Please check the featureview details for information about data sync into the feature store.")

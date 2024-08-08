import sys

from google.cloud import bigquery

from constants import TFVARS

data = sys.argv[1]

bq_client = bigquery.Client()
project_prefix = TFVARS["project"].replace("-", "_")
data_table = bq_client.get_table(f"{TFVARS['project']}.{project_prefix}_database.data_table")

last_id_query = bq_client.query(f"SELECT max(id) as max_id from {data_table}")
last_id = None
for lid in last_id_query.result():
    last_id = lid.get("max_id", 0)

last_id = last_id if last_id is not None else 0

data_point = {"id": last_id + 1, "data": data}
errors = bq_client.insert_rows_json(data_table, [data_point])

if errors is not None and len(errors) > 0:
    print(f"Error saving data to table: {errors}")
else:
    print(f"Data point added: {data_point}")

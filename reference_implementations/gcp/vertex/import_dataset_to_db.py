import json
import argparse

from google.cloud import bigquery
import pandas as pd
from constants import TFVARS



# --------- Load the meta data
storage_directory = "../../../data"
with open(f"{storage_directory}/meta.json", "r") as f:
    meta_data = json.load(f)

keys = meta_data.keys()
parser = argparse.ArgumentParser(description="Parser for cmdline arguments")
parser.add_argument('--datasetname', type=str, required=True, help=f"choose from {str(list(keys))}")
args = parser.parse_args()
# 

# ----------- Load selected dataset

selected_ds = args.datasetname
ds_meta = meta_data[selected_ds]


upload_data = {}
data_file_to_load = f"{storage_directory}/{selected_ds}/{selected_ds}.json"
print(f'Data file to load: {data_file_to_load}')
# with open(data_file_to_load) as f:
#     df = json.load(f)

df = pd.read_json(data_file_to_load)
print(df.columns)


# supported_task_types = ["Summarization", "Translation", "Classification"]
# task_type = meta_data[args.datasetname]["type"]
# if task_type not in supported_task_types:
#     print(f"Task type '{task_type}' is not supported. Supported task types: {supported_task_types}")
#     exit()

# ------- Get max Ids in BQ tables
bq_client = bigquery.Client()
project_prefix = TFVARS["project"].replace("-", "_")
data_table = bq_client.get_table(f"{TFVARS['project']}.{project_prefix}_{TFVARS['env']}_database.data_table")
ground_truth_table = bq_client.get_table(f"{TFVARS['project']}.{project_prefix}_{TFVARS['env']}_database.ground_truth_table")

last_id = bq_client.query(f"SELECT max(id) as max_id from {data_table}").to_dataframe()
last_gt_id = bq_client.query(f"SELECT max(id) as max_id from {ground_truth_table}").to_dataframe()

last_id = last_id["max_id"].values[0] if last_id is not None else 0
last_gt_id = last_gt_id["max_id"].values[0] if last_gt_id is not None else 0

# for lid in last_id_query.result():
#     last_id = lid.get("max_id", 0)

# for lid in last_gt_id_query.result():
#     last_gt_id = lid.get("max_id", 0)

# last_id = last_id if last_id is not None else 0
# last_gt_id = last_gt_id if last_gt_id is not None else 0


# ------ Add ID to data_table
data_df = df.copy()
data_df.drop(columns=['id', ds_meta["gt"]], inplace=True, errors='ignore')
ids = [i for i in range(last_id+1, last_id+1+len(data_df))]
if ds_meta["type"] in ["Translation", "Summarization"]: # for compatability with examples
    data_df.rename(columns={'article': 'data'}, inplace=True)  
data_df["id"] = ids

# ------ Add ID to ground_truth_table
gt_df = df[[ds_meta["gt"]]].copy()
gt_df.rename(columns={ds_meta["gt"]: 'ground_truth'}, inplace=True)
# Keeping id and data_id same, can't have more gt than data points
gt_df["id"] = ids
gt_df["data_id"] = ids


# ------ Write to BQ
data_job = bq_client.load_table_from_dataframe(data_df, data_table, 
                    job_config=bigquery.LoadJobConfig(write_disposition="WRITE_APPEND"))

gt_job = bq_client.load_table_from_dataframe(gt_df, ground_truth_table, 
                    job_config=bigquery.LoadJobConfig(write_disposition="WRITE_APPEND"))


# -------- Check for errors
if data_job.errors is not None and len(data_job.errors) > 0:
    print(f"Error saving data to table: {data_job.errors}")

if data_job.errors is not None and len(gt_job.errors) > 0:
    print(f"Error saving data to table: {gt_job.errors}")

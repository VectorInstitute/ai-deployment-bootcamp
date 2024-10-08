import json
import argparse

from google.cloud import bigquery

from constants import TFVARS

storage_directory = "../../../data"
with open(f"{storage_directory}/meta.json", "r") as f:
    meta_data = json.load(f)

keys = meta_data.keys()

parser = argparse.ArgumentParser(description="Parser for cmdline arguments")
parser.add_argument('--datasetname', type=str, required=True, help=f"choose from {str(list(keys))}")
args = parser.parse_args()

upload_data = {}
with open(f"{storage_directory}/{args.datasetname}/{args.datasetname}.json") as f:
    df = json.load(f)

supported_task_types = ["Summarization", "Translation"]
task_type = meta_data[args.datasetname]["type"]
if task_type not in supported_task_types:
    print(f"Task type '{task_type}' is not supported. Supported task types: {supported_task_types}")
    exit()

bq_client = bigquery.Client()
project_prefix = TFVARS["project"].replace("-", "_")
data_table = bq_client.get_table(f"{TFVARS['project']}.{project_prefix}_{TFVARS['env']}_database.data_table")
ground_truth_table = bq_client.get_table(f"{TFVARS['project']}.{project_prefix}_{TFVARS['env']}_database.ground_truth_table")

last_id_query = bq_client.query(f"SELECT max(id) as max_id from {data_table}")
last_gt_id_query = bq_client.query(f"SELECT max(id) as max_id from {ground_truth_table}")
last_id = None

for lid in last_id_query.result():
    last_id = lid.get("max_id", 0)

for lid in last_gt_id_query.result():
    last_gt_id = lid.get("max_id", 0)

last_id = last_id if last_id is not None else 0
last_gt_id = last_gt_id if last_gt_id is not None else 0
data_list = []
gt_list = []
for i in range(len(df)):
    if task_type == ("Summarization"):
        data = df[i][meta_data[args.datasetname]["data"]]
        gt = df[i][meta_data[args.datasetname]["gt"]]

    elif task_type == "Translation":
        base_key = meta_data[args.datasetname]["data"][0]
        data = df[i][base_key][meta_data[args.datasetname]["data"][1]]
        gt = df[i][base_key][meta_data[args.datasetname]["gt"][1]]
    
    data_point = {"id": last_id + 1, "data": data}
    data_list.append(data_point)
    gt_point = {"id": last_gt_id + 1,"data_id": last_id+1, "ground_truth": gt}
    gt_list.append(gt_point)
    last_id += 1
    last_gt_id += 1
    
errors = bq_client.insert_rows_json(data_table, data_list)
errors_gt = bq_client.insert_rows_json(ground_truth_table, gt_list)

if errors is not None and len(errors) > 0:
    print(f"Error saving data to table: {errors}")
else:
    print(f"Data point added: {data_point}")

if errors_gt is not None and len(errors_gt) > 0:
    print(f"Error saving data to table: {errors_gt}")
else:
    print(f"Data point added: {gt_point}")
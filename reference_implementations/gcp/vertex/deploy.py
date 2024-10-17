import logging
import sys

from google.cloud import aiplatform, bigquery
from vertexai.resources.preview import ml_monitoring

from constants import TFVARS, TFVARS_PATH, PROJECT_NUMBER, DOCKER_REPO_NAME, DOCKER_IMAGE_NAME
from utils import save_tfvars


model_id = sys.argv[1] if len(sys.argv) > 1 else None
model_version = sys.argv[2] if len(sys.argv) > 2 else "default"

model_name = "diabetes_randomforest_pipeline" ###
hf_task = "RandomForestClassifier" ###

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s")

project_prefix = TFVARS["project"].replace("-", "_")
endpoint_display_name = f"{project_prefix}_{TFVARS['env']}_endpoint"
bq_logging_dataset = f"{endpoint_display_name}_monitoring"
bq_logging_table = f"bq://{TFVARS['project']}.{bq_logging_dataset}.req_resp"

aiplatform.init(project=TFVARS["project"], location=TFVARS["region"])


if model_id is not None:
    model = aiplatform.Model(f"projects/{PROJECT_NUMBER}/locations/{TFVARS['region']}/models/{model_id}@{model_version}")
else:
    model = aiplatform.Model.upload(
        display_name=model_name,
        artifact_uri=f"gs://{TFVARS['project']}-model/{model_name}",
        serving_container_image_uri=f"{TFVARS['region']}-docker.pkg.dev/{TFVARS['project']}/{DOCKER_REPO_NAME}/{DOCKER_IMAGE_NAME}:latest",
        serving_container_environment_variables={
            "HF_TASK": hf_task,
            "VERTEX_CPR_WEB_CONCURRENCY": 1,
        },
    )

# Create BigQuery logging table if it doesn't exist
bq_client = bigquery.Client()
dataset_ids = [dataset.dataset_id for dataset in list(bq_client.list_datasets())]
if bq_logging_dataset not in dataset_ids:
    bq_dataset = bigquery.Dataset(f"{TFVARS['project']}.{bq_logging_dataset}")
    bq_dataset.location = "US"
    bq_dataset = bq_client.create_dataset(bq_dataset, timeout=30)

endpoint = aiplatform.Endpoint.create(
    display_name=endpoint_display_name,
    enable_request_response_logging=True,
    request_response_logging_sampling_rate=1.0,
    request_response_logging_bq_destination_table=bq_logging_table,
)

# Saving the endpoint id and model name in the tfvars
TFVARS["endpoint"] = endpoint.name
TFVARS["model"] = model_name
save_tfvars(TFVARS, TFVARS_PATH)

# we will use the n1-standard-4 from the N1-Series that comes with GPU acceleration
# with an NVIDIA Tesla T4, 4 vCPUs and 15 GB of RAM memory
deployed_endpoint = model.deploy(
    endpoint=endpoint,
    machine_type="n1-standard-4",
    # GPU type
    accelerator_type="NVIDIA_TESLA_T4",
    # Number of GPUs
    accelerator_count=1,
    # auto-scaling
    max_replica_count=1,
)

model_monitoring_schema = ml_monitoring.spec.ModelMonitoringSchema(
    feature_fields=[
        ml_monitoring.spec.FieldSchema(name="id", data_type="integer"),
        ml_monitoring.spec.FieldSchema(name="data_feature", data_type="string"),
    ],
    ground_truth_fields=[
        ml_monitoring.spec.FieldSchema(name="label", data_type="categorical"),
    ],
    prediction_fields=[
        ml_monitoring.spec.FieldSchema(name="predicted_label", data_type="categorical"),
    ],
)

# Optional: feed in a training dataset

model_monitor = ml_monitoring.ModelMonitor.create(
    project=TFVARS["project"],
    location=TFVARS["region"],
    display_name=f"bart_model_monitor_{TFVARS['env']}",
    model_name=model.resource_name,
    model_version_id=model_version,
    # training_dataset=TRAINING_DATASET,
    model_monitoring_schema=model_monitoring_schema,
)
print(f"Model monitor {model_monitor.name} created.")

print("Endpoint ID:", endpoint.name)

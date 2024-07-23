import sys

from google.cloud import aiplatform
from vertexai.resources.preview import ml_monitoring

from utils import get_project_number, load_tfvars, save_tfvars

# Load TF Vars
TFVARS_PATH = "../architectures/terraform.tfvars"
tfvars = load_tfvars(TFVARS_PATH)

MODEL_NAME = "bart-large-mnli"
DOCKER_REPO_NAME = f"{tfvars['project']}-docker-repo"
DOCKER_IMAGE_NAME = f"{tfvars['project']}-inferencer"

project_number = get_project_number(tfvars["project"])
endpoint_display_name = f"bart-large-mnli_endpoint"
bq_logging_dataset = "bart_large_mnli_monitoring"
bq_logging_table = f"bq://{tfvars['project']}.{bq_logging_dataset}.req_resp"

aiplatform.init(project=tfvars["project"], location=tfvars["region"])

model_id = sys.argv[1] if len(sys.argv) > 1 else None
model_version = sys.argv[2] if len(sys.argv) > 2 else "default"

if model_id is not None:
    model = aiplatform.Model(f"projects/{project_number}/locations/{tfvars['region']}/models/{model_id}@{model_version}")
else:
    model = aiplatform.Model.upload(
        display_name=MODEL_NAME,
        artifact_uri=f"gs://{tfvars['project']}/model",
        serving_container_image_uri=f"{tfvars['region']}-docker.pkg.dev/{tfvars['project']}/{DOCKER_REPO_NAME}/{DOCKER_IMAGE_NAME}:latest",
        serving_container_environment_variables={
            "HF_TASK": "zero-shot-classification",
            "VERTEX_CPR_WEB_CONCURRENCY": 1,
        },
    )

endpoint = aiplatform.Endpoint.create(
    display_name=endpoint_display_name,
    enable_request_response_logging=True,
    request_response_logging_sampling_rate=1.0,
    request_response_logging_bq_destination_table=bq_logging_table,
)

# Saving the endpoint id in the tfvars
tfvars["endpoint"] = endpoint.name
save_tfvars(tfvars, TFVARS_PATH)

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

print(f"Endpoint resource name: {deployed_endpoint.resource_name}")

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
    project=tfvars["project"],
    location=tfvars["region"],
    display_name="bart_model_monitor",
    model_name=model.resource_name,
    model_version_id=model_version,
    # training_dataset=TRAINING_DATASET,
    model_monitoring_schema=model_monitoring_schema,
)
print(f"Model monitor {model_monitor.name} created.")

# TODO run the model monitoring jobs


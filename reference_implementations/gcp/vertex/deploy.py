import sys

from google.cloud import aiplatform
from vertexai.resources.preview import ml_monitoring

from constants import TFVARS, TFVARS_PATH, PROJECT_NUMBER, DOCKER_REPO_NAME, DOCKER_IMAGE_NAME, MODEL_NAME
from utils import save_tfvars


endpoint_display_name = f"bart-large-mnli_endpoint"
bq_logging_dataset = "bart_large_mnli_monitoring"
bq_logging_table = f"bq://{TFVARS['project']}.{bq_logging_dataset}.req_resp"

aiplatform.init(project=TFVARS["project"], location=TFVARS["region"])

model_id = sys.argv[1] if len(sys.argv) > 1 else None
model_version = sys.argv[2] if len(sys.argv) > 2 else "default"

if model_id is not None:
    model = aiplatform.Model(f"projects/{PROJECT_NUMBER}/locations/{TFVARS['region']}/models/{model_id}@{model_version}")
else:
    model = aiplatform.Model.upload(
        display_name=MODEL_NAME,
        artifact_uri=f"gs://{TFVARS['project']}/model",
        serving_container_image_uri=f"{TFVARS['region']}-docker.pkg.dev/{TFVARS['project']}/{DOCKER_REPO_NAME}/{DOCKER_IMAGE_NAME}:latest",
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
TFVARS["endpoint"] = endpoint.name
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
    project=TFVARS["project"],
    location=TFVARS["region"],
    display_name="bart_model_monitor",
    model_name=model.resource_name,
    model_version_id=model_version,
    # training_dataset=TRAINING_DATASET,
    model_monitoring_schema=model_monitoring_schema,
)
print(f"Model monitor {model_monitor.name} created.")

# TODO run the model monitoring jobs


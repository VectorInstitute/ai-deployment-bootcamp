import sys

from google.cloud import aiplatform
from vertexai.resources.preview import ml_monitoring


aiplatform.init(project="ai-deployment-bootcamp", location="us-west2")

model_id = sys.argv[1] if len(sys.argv) > 1 else None
model_version = sys.argv[2] if len(sys.argv) > 2 else "1"

if model_id is not None:
    model = aiplatform.Model(f"projects/761003357790/locations/us-west2/models/{model_id}@{model_version}")
else:
    model = aiplatform.Model.upload(
        display_name="bart-large-mnli",
        artifact_uri="gs://ai-deployment-bootcamp/model",
        serving_container_image_uri="us-west2-docker.pkg.dev/ai-deployment-bootcamp/ai-deployment-bootcamp-docker-repo/ai-deployment-bootcamp-inferencer:latest",
        serving_container_environment_variables={
            "HF_TASK": "zero-shot-classification",
            "VERTEX_CPR_WEB_CONCURRENCY": 1,
        },
    )

endpoint_display_name = f"bart-large-mnli_endpoint"
bq_logging_dataset = "bart_large_mnli_monitoring"
bq_logging_table = f"bq://ai-deployment-bootcamp.{bq_logging_dataset}.req_resp"

endpoint = aiplatform.Endpoint.create(
    display_name=endpoint_display_name,
    enable_request_response_logging=True,
    request_response_logging_sampling_rate=1.0,
    request_response_logging_bq_destination_table=bq_logging_table,
)

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
    max_replica_count=10,
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
    project="ai-deployment-bootcamp",
    location="us-west2",
    display_name="bart_model_monitor",
    model_name=model.resource_name,
    model_version_id=model_version,
    # training_dataset=TRAINING_DATASET,
    model_monitoring_schema=model_monitoring_schema,
)
print(f"Model monitor {model_monitor.name} created.")

# TODO run the model monitoring jobs

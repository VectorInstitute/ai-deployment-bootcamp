import json
import sys

from google.cloud import aiplatform

aiplatform.init(project="ai-deployment-bootcamp", location="us-west2")

model_id = sys.argv[1] if len(sys.argv) > 1 else None
model_version = sys.argv[2] if len(sys.argv) > 2 else "1"

if model_id is not None:
    model = aiplatform.Model(f"projects/761003357790/locations/us-west2/models/{model_id}@{model_version}")
else:
    model = aiplatform.Model.upload(
        display_name="bart-large-mnli",
        artifact_uri="gs://ai-deployment-bootcamp",
        serving_container_image_uri="us-west2-docker.pkg.dev/ai-deployment-bootcamp/ai-deployment-bootcamp-docker-repo/ai-deployment-bootcamp-inferencer:latest",
        serving_container_environment_variables={
            "HF_TASK": "zero-shot-classification",
            "VERTEX_CPR_WEB_CONCURRENCY": 1,
        },
    )

# we will use the n1-standard-4 from the N1-Series that comes with GPU acceleration
# with an NVIDIA Tesla T4, 4 vCPUs and 15 GB of RAM memory
endpoint = model.deploy(
    machine_type="n1-standard-4",
    accelerator_type="NVIDIA_TESLA_T4",
    accelerator_count=1,
)

print(f"Endpoint resource name: {endpoint.resource_name}")

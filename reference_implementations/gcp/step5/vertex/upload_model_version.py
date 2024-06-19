import sys

from google.cloud import aiplatform


model_id = sys.argv[1]
artifact_uri = sys.argv[2]

aiplatform.init(project="ai-deployment-bootcamp", location="us-west2")

model = aiplatform.Model(f"projects/761003357790/locations/us-west2/models/{model_id}")
model_v2 = aiplatform.Model.upload(
    parent_model=model.resource_name,
    display_name="bart-large-mnli",
    artifact_uri=artifact_uri,
    serving_container_image_uri="us-west2-docker.pkg.dev/ai-deployment-bootcamp/ai-deployment-bootcamp-docker-repo/ai-deployment-bootcamp-inferencer:latest",
    serving_container_environment_variables={
        "HF_TASK": "zero-shot-classification",
        "VERTEX_CPR_WEB_CONCURRENCY": 1,
    },
)

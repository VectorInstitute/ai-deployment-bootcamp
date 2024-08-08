import sys
import logging

from google.cloud import aiplatform

from constants import TFVARS, PROJECT_NUMBER, DOCKER_REPO_NAME, DOCKER_IMAGE_NAME, MODEL_NAME

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

model_id = sys.argv[1]
artifact_uri = sys.argv[2]

aiplatform.init(project=TFVARS["project"], location=TFVARS["region"])

logger.info("Uploading new model version...")

model = aiplatform.Model(f"projects/{PROJECT_NUMBER}/locations/{TFVARS['region']}/models/{model_id}")
model_v2 = aiplatform.Model.upload(
    parent_model=model.resource_name,
    display_name=MODEL_NAME,
    artifact_uri=artifact_uri,
    serving_container_image_uri=f"{TFVARS['region']}-docker.pkg.dev/{TFVARS['project']}/{DOCKER_REPO_NAME}/{DOCKER_IMAGE_NAME}:latest",
    serving_container_environment_variables={
        "HF_TASK": "zero-shot-classification",
        "VERTEX_CPR_WEB_CONCURRENCY": 1,
    },
)

endpoint = aiplatform.models.Endpoint(
    endpoint_name=f"projects/{PROJECT_NUMBER}/locations/{TFVARS['region']}/endpoints/{TFVARS['endpoint']}",
)

deployed_models = endpoint.list_models()

logger.info("Deploying new model version...")
endpoint.deploy(
    model_v2,
    traffic_percentage=100,
    machine_type="n1-standard-4",
    accelerator_type="NVIDIA_TESLA_T4",
    accelerator_count=1,
    max_replica_count=1,
)

for deployed_model in deployed_models:
    model_id = deployed_model.id
    logger.info(f"Undeploying model id {model_id}")
    endpoint.undeploy(model_id)

logger.info("Done.")

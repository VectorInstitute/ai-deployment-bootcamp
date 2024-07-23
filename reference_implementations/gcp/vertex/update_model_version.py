import sys
import logging

from google.cloud import aiplatform

from utils import load_tfvars, get_project_number

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


# Load TF Vars
TFVARS_PATH = "../architectures/terraform.tfvars"
tfvars = load_tfvars(TFVARS_PATH)
project_number = get_project_number(tfvars["project"])

MODEL_NAME = "bart-large-mnli"
DOCKER_REPO_NAME = f"{tfvars['project']}-docker-repo"
DOCKER_IMAGE_NAME = f"{tfvars['project']}-inferencer"

model_id = sys.argv[1]
artifact_uri = sys.argv[2]

aiplatform.init(project=tfvars["project"], location=tfvars["region"])

logger.info("Uploading new model version...")

model = aiplatform.Model(f"projects/{project_number}/locations/{tfvars['region']}/models/{model_id}")
model_v2 = aiplatform.Model.upload(
    parent_model=model.resource_name,
    display_name=MODEL_NAME,
    artifact_uri=artifact_uri,
    serving_container_image_uri=f"{tfvars['region']}-docker.pkg.dev/{tfvars['project']}/{DOCKER_REPO_NAME}/{DOCKER_IMAGE_NAME}:latest",
    serving_container_environment_variables={
        "HF_TASK": "zero-shot-classification",
        "VERTEX_CPR_WEB_CONCURRENCY": 1,
    },
)

endpoint = aiplatform.models.Endpoint(
    endpoint_name=f"projects/761003357790/locations/us-west2/endpoints/{tfvars['endpoint']}",
)

deployed_models = endpoint.list_models()

logger.info("Deploying new model version...")
endpoint.deploy(
    model_v2,
    traffic_percentage=100,
    machine_type="n1-standard-4",
    accelerator_type="NVIDIA_TESLA_T4",
    accelerator_count=1,
    max_replica_count=10,
)

for deployed_model in deployed_models:
    model_id = deployed_model.id
    logger.info(f"Undeploying model id {model_id}")
    endpoint.undeploy(model_id)

logger.info("Done.")

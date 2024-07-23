from google.cloud.aiplatform.prediction import LocalModel

from predictor import HuggingFacePredictor

from utils import load_tfvars

# Load TF Vars
TFVARS_PATH = "../architectures/terraform.tfvars"
tfvars = load_tfvars(TFVARS_PATH)

MODEL_NAME = "bart-large-mnli"
DOCKER_REPO_NAME = f"{tfvars['project']}-docker-repo"
DOCKER_IMAGE_NAME = f"{tfvars['project']}-inferencer"

local_model = LocalModel.build_cpr_model(
    "./",
    f"{tfvars['region']}-docker.pkg.dev/{tfvars['project']}/{DOCKER_REPO_NAME}/{DOCKER_IMAGE_NAME}:latest",
    predictor=HuggingFacePredictor,
    requirements_path="./requirements.txt",
    base_image="--platform=linux/amd64 alvarobartt/torch-gpu:py310-cu12.3-torch-2.2.0 AS build",
)
local_model.push_image()

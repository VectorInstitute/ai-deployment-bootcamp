import logging

from google.cloud.aiplatform.prediction import LocalModel

# from predictor.hf_predictor import HuggingFacePredictor
from predictor.hf_predictor import SklearnPredictor

from constants import TFVARS, DOCKER_REPO_NAME, DOCKER_IMAGE_NAME

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s")

local_model = LocalModel.build_cpr_model(
    "./predictor",
    f"{TFVARS['region']}-docker.pkg.dev/{TFVARS['project']}/{DOCKER_REPO_NAME}/{DOCKER_IMAGE_NAME}:latest",
    predictor=SklearnPredictor,
    requirements_path="./predictor/requirements.txt",
    base_image="--platform=linux/amd64 alvarobartt/torch-gpu:py310-cu12.3-torch-2.2.0 AS build",
)
local_model.push_image()

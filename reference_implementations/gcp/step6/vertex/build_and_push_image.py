from google.cloud.aiplatform.prediction import LocalModel

from predictor import HuggingFacePredictor

local_model = LocalModel.build_cpr_model(
    "./",
    "us-west2-docker.pkg.dev/ai-deployment-bootcamp/ai-deployment-bootcamp-docker-repo/ai-deployment-bootcamp-inferencer:latest",
    predictor=HuggingFacePredictor,
    requirements_path="./requirements.txt",
    base_image="--platform=linux/amd64 alvarobartt/torch-gpu:py310-cu12.3-torch-2.2.0 AS build",
)
local_model.push_image()

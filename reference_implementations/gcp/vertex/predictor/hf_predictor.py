import os
import logging
import tarfile
from typing import Any, Dict

from transformers import pipeline

from google.cloud.aiplatform.prediction.predictor import Predictor
from google.cloud.aiplatform.utils import prediction_utils

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class HuggingFacePredictor(Predictor):
    def __init__(self) -> None:
        pass

    def load(self, artifacts_uri: str) -> None:
        """Loads the preprocessor and model artifacts."""
        logger.info(f"Downloading artifacts from {artifacts_uri}")
        prediction_utils.download_model_artifacts(artifacts_uri)
        logger.info("Artifacts successfully downloaded!")

        os.makedirs("./model", exist_ok=True)
        with tarfile.open("model.tar.gz", "r:gz") as tar:
            tar.extractall(path="./model")

        logger.info(f"HF_TASK value is {os.getenv('HF_TASK')}")
        self._pipeline = pipeline(os.getenv("HF_TASK", ""), model="./model", device_map="auto")
        logger.info("`pipeline` successfully loaded!")

        logger.info(f"`pipeline` is using device={self._pipeline.device}")

    def predict(self, instances: Dict[str, Any]) -> Dict[str, Any]:
        return self._pipeline(**instances)

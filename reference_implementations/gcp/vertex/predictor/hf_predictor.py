import joblib
import numpy as np
import os
import pickle
import logging

from google.cloud.aiplatform.constants import prediction
from google.cloud.aiplatform.utils import prediction_utils
from google.cloud.aiplatform.prediction.predictor import Predictor

from model_training.preprocessing import TypeTransformer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SklearnPredictor(Predictor):

    def __init__(self):
        return
    
    def load(self, artifacts_uri: str) -> None:
        prediction_utils.download_model_artifacts(artifacts_uri)
        model_path = "./diabetes_randomforest_pipeline.pkl"
        logger.info(f">>>> Loading model from: {model_path}")
        self._model = joblib.load(model_path)
        
        logger.info(f">>>> Model is loaded successfully")

    def predict(self, instances: np.ndarray) -> np.ndarray:
        return self._model.predict(instances)
    
    # def preprocess(self, prediction_input: dict) -> np.ndarray:
    #     logger.info(">>>> preprocess started")
    #     instances = prediction_input["instances"]
    #     logger.info(">>>> preprocess returning")
    #     return np.asarray(instances)

    # def postprocess(self, prediction_results: np.ndarray) -> dict:
    #     logger.info(">>>> postprocess started and returning")
    #     return {"predictions": prediction_results.tolist()}

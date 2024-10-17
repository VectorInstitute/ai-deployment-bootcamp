import joblib
import numpy as np
import os
import pickle
import logging

from google.cloud.aiplatform.constants import prediction
from google.cloud.aiplatform.utils import prediction_utils
from google.cloud.aiplatform.prediction.predictor import Predictor
from sklearn.base import BaseEstimator, TransformerMixin

from .custom_model import TypeTransformer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TypeTransformer(BaseEstimator, TransformerMixin):
    def transform(self, X):
        X = X.astype(int)
        return X


class SklearnPredictor(Predictor):

    def __init__(self):
        return
    
    def load(self, artifacts_uri: str) -> None:
        prediction_utils.download_model_artifacts(artifacts_uri)
        model_path = "./diabetes_randomforest_pipeline.pkl"
        # model_path = "./model.pkl"
        logger.info(f">>>> Loading model from: {model_path}")
        self._model = joblib.load(model_path)
        
        # logger.info(f">>>> prediction.MODEL_FILENAME_JOBLIB: {prediction.MODEL_FILENAME_JOBLIB}")
        # logger.info(f">>>> prediction.MODEL_FILENAME_PKL: {prediction.MODEL_FILENAME_PKL}")
        # if os.path.exists(prediction.MODEL_FILENAME_JOBLIB):
        #     logger.info(">>>>TRUE: os.path.exists(prediction.MODEL_FILENAME_JOBLIB)")
        #     self._model = joblib.load(prediction.MODEL_FILENAME_JOBLIB)
        # elif os.path.exists(prediction.MODEL_FILENAME_PKL):
        #     logger.info(">>>>TRUE: os.path.exists(prediction.MODEL_FILENAME_PKL)")
        #     self._model = pickle.load(open(prediction.MODEL_FILENAME_PKL, "rb"))
        # else:
        #     logger.info(f">>>>In ELSE: One of the following model files must be provided")
        #     self._model = pickle.load(open(model_path, "rb"))

    # def preprocess(self, prediction_input: dict) -> np.ndarray:
    #     logger.info(">>>> preprocess started")
    #     instances = prediction_input["instances"]
    #     logger.info(">>>> preprocess returning")
    #     return np.asarray(instances)

    def predict(self, instances: np.ndarray) -> np.ndarray:
        return self._model.predict(instances)

    # def postprocess(self, prediction_results: np.ndarray) -> dict:
    #     logger.info(">>>> postprocess started and returning")
    #     return {"predictions": prediction_results.tolist()}

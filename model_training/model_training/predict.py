import pandas as pd 
from model_training.preprocessing import TypeTransformer
from model_training.config import SAMPLE_DATA_PATH, MODEL_PATH
import joblib


pipeline = joblib.load(MODEL_PATH)

data = pd.read_csv(SAMPLE_DATA_PATH)

y_pred = pipeline.predict(data)
print('Predictions: ', y_pred)
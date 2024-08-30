from datetime import datetime, timedelta

import boto3
import json
import sagemaker
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sagemaker.predictor import Predictor

# Create a SageMaker Predictor object (replace role with your actual role)
# role = 'your-role-arn'  # IAM role with access to SageMaker endpoint
try:
	role = sagemaker.get_execution_role()
except ValueError:
	iam = boto3.client('iam')
	role = iam.get_role(RoleName='sagemaker_execution_role')['Role']['Arn']

print(f"Role: \n{role=}")

endpoint_name = 'paraphrase-bert-en-inf1-202408-2112-1958'
region = "us-east-1"

predictor = Predictor(endpoint_name=endpoint_name, role=role)

app = FastAPI()

def predict(data):
    """
    Makes predictions using the SageMaker Predictor.

    Args:
        data (dict): Input data for the model.

    Returns:
        dict: Prediction results.
    """
    input_data_json = json.dumps(data)

    # Send the data to the SageMaker endpoint for prediction
    response = predictor.predict(input_data_json)

    # Handle response (may require specific processing based on your model)
    print(f"\n{response=}\n")
    result_str = response.decode('utf-8')

    return result_str

@app.post("/predict")
async def predict_endpoint(data: dict):
    """
    API endpoint for receiving prediction requests.

    Args:
        data (dict): Input data in JSON format.

    Returns:
        JSONResponse: Prediction results in JSON format.
    """

    result = predict(data)
    return JSONResponse(result)

@app.get("/")
async def home():
      """
      API endpoint to confirm the api is running.
      """
      result = "Hello and welcome to Vector's AI Deployment Bootcamp!"
      return JSONResponse(result)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


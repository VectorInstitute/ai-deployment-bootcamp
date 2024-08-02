from fastapi import FastAPI, Request, JSONResponse
import boto3
from sagemaker.predictor import Predictor

# Replace with your SageMaker endpoint name
endpoint_name = 'my-bart-endpoint'

# Create a SageMaker Predictor object (replace role with your actual role)
role = 'your-role-arn'  # IAM role with access to SageMaker endpoint
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

    # Send the data to the SageMaker endpoint for prediction
    response = predictor.predict(data)

    # Handle response (may require specific processing based on your model)
    return response

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


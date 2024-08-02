from fastapi import FastAPI, Request, JSONResponse
import boto3
from sagemaker.predictor import Predictor

# Replace with your SageMaker endpoint name
endpoint_name = 'ai-deployment-endpoint'

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

## Another approach:
    
# import boto3
# import json

# # Initialize the SageMaker runtime client
# runtime_client = boto3.client('sagemaker-runtime', region_name='<your-region>')

# # Define the SageMaker endpoint name (ensure it matches the one created by Terraform)
# endpoint_name = "my-endpoint"

# # Example input data for model inference
# input_data = {
#     # Your input data goes here
# }

# # Convert input data to JSON string
# payload = json.dumps(input_data)

# # Invoke the SageMaker endpoint
# response = runtime_client.invoke_endpoint(
#     EndpointName=endpoint_name,
#     ContentType='application/json',
#     Body=payload
# )

# # Parse the response
# result = json.loads(response['Body'].read().decode())

# print("Model inference result:", result)

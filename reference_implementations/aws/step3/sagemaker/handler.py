import json
from transformers import pipeline
import os
from sagemaker.session import Session

## TODO: Remove if not required.
def handle_request(data, context):
  """Handles incoming requests, loads the model using pipeline, and makes predictions."""

  # Create a SageMaker session
  session = Session()

  # Get model data path from environment variable
  model_data_dir = os.environ.get('MODEL_DATA_DIR')

  # Load the pre-trained model using transformers pipeline
  model_path = os.path.join(model_data_dir, 'model.safetensors')  # Adjust if needed
  pipeline_model = pipeline("text-classification", model=model_path)

  # Parse input data (assuming JSON format)
  if 'application/json' in context.headers.get('Content-Type', ''):
    input_data = json.loads(data.body.decode('utf-8'))
  else:
    # Handle other content types if necessary
    pass

  # Make predictions
  predictions = pipeline_model(input_data)

  # Output predictions as JSON (adjust based on your model's output format)
  response_body = json.dumps(predictions)
  return {
      'statusCode': 200,
      'body': response_body,
      'headers': {
          'Content-Type': 'application/json'
      }
  }

# handler.py - old version
# import json
# import os
# import boto3
# from sagemaker.predictor import Predictor

# def model_fn(model_dir):
#     """
#     Loads the model into memory.

#     Args:
#         model_dir (str): Path to the model directory.
#     """
#     # Implement model loading logic here
#     # Example using PyTorch:
#     import torch
#     model = torch.load(os.path.join(model_dir, 'model.pt'))
#     return model

# def input_fn(request_body, request_content_type):
#     """
#     Parses input data.

#     Args:
#         request_body (str): The body of the request.
#         request_content_type (str): The content type of the request.

#     Returns:
#         dict: Parsed input data.
#     """

#     if request_content_type == 'application/json':
#         return json.loads(request_body)
#     else:
#         # Handle other content types
#         pass

# def output_fn(prediction, content_type):
#     """
#     Formats the prediction output.

#     Args:
#         prediction (any): The prediction result.
#         content_type (str): The desired content type for the response.

#     Returns:
#         str: The formatted prediction output.
#     """

#     if content_type == 'application/json':
#         return json.dumps(prediction)
#     else:
#         # Handle other content types
#         pass

# def predict_fn(data, model):
#     """
#     Makes predictions using the loaded model.

#     Args:
#         data (dict): Input data.
#         model (object): Loaded model.

#     Returns:
#         dict: Prediction results.
#     """

#     # Replace with your prediction logic
#     # Example using Hugging Face pipeline:
#     model_path = "/opt/ml/model"  # Replace with actual model path if necessary
#     pipeline_model = pipeline("text-classification", model=model_path)
#     predictions = pipeline_model(data)
#     return predictions

# def handle_request(data, context):
#     """
#     Handles incoming requests.

#     Args:
#         data (dict): Input data.
#         context (object): Request context.

#     Returns:
#         dict: Prediction results.
#     """

#     # Load the model
#     model = model_fn(context.model_dir)

#     # Preprocess input data
#     input_data = input_fn(data, 'application/json')

#     # Make predictions
#     prediction = predict_fn(input_data, model)

#     # Post-process output
#     response = output_fn(prediction, 'application/json')

#     return response

#!/bin/bash
# How to run this script in the terminal:
# bash reference_implementations\gcp\architectures\online\ml-api\startup.sh
# Define variables
PROJECT_ID="bell-canada-inc"
SHORT_PROJECT_ID="bci" # Replace with your project ID
USER="lp-test" # Replace with your username
BUCKET_NAME="${SHORT_PROJECT_ID}-${USER}-ai-deployment-bootcamp-model"
MODEL_SOURCE="gs://vertex-model-garden-public-us/llama3.1"
LOCATION="us-central1"
MODEL_ID="" # Optional: Fill this if you have a specific model ID to deploy
MODEL_VERSION="" # Optional: Fill this if you have a specific model version to deploy
ENDPOINT_ID="" # Optional: Fill this if you have a known endpoint ID for testing or undeploying

# Step 1: Copy the Model to Cloud Storage
gcloud storage buckets create gs://${BUCKET_NAME} --location=${LOCATION} --project=${PROJECT_ID}
gsutil -m cp -R ${MODEL_SOURCE} gs://${BUCKET_NAME}/llama-garden

# Step 2: Deploy the Model to an Endpoint
if [ -z "$MODEL_ID" ]; then
    python -m deploy_llama_3_1_from_garden
else
    python -m deploy_llama_3_1_from_garden $MODEL_ID $MODEL_VERSION
fi

# Optional: Test the Endpoint
# Uncomment and set the ENDPOINT_ID variable if known
# python -m test_endpoint "inputs/llama3.1.json" $ENDPOINT_ID

# Optional: Undeploy
# Uncomment and set the ENDPOINT_ID variable if you wish to undeploy
# python -m undeploy $ENDPOINT_ID
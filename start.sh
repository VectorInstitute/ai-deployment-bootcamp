#!/bin/bash
# How to run this script in the terminal:
# bash start.sh

# Extract the user variable value from terraform.tfvars
user_email=$(grep "^user\s*=" reference_implementations/gcp/architectures/terraform.tfvars | cut -d'"' -f2)

# Check if the user variable is empty
if [ -z "$user_email" ]; then
    # Prompt for user email
    read -p "Enter user email: " user_email
    # Optionally, you can update the terraform.tfvars file with the new user email
    # sed -i 's/^user\s*=.*/user = "'$user_email'"/' reference_implementations/gcp/architectures/terraform.tfvars
fi

# Extract the part before the @ of the user email
user_prefix=$(echo "$user_email" | cut -d '@' -f 1)
shortened_user_name=$(echo "$user_prefix" | awk -F'[._]' '{print substr($1,1,1) substr($2,1,1)}')

# Update terraform.tfvars file with the user email and a constructed env value
sed -i "s/^user =.*/user = \"$user_email\"/" reference_implementations/gcp/architectures/terraform.tfvars
sed -i "s/^shortened_user_name =.*/shortened_user_name = \"$shortened_user_name\"/" reference_implementations/gcp/architectures/terraform.tfvars
sed -i "s/^env =.*/env = \"dev-$user_prefix\"/" reference_implementations/gcp/architectures/terraform.tfvars

# Navigate to the vertex directory
cd ./reference_implementations/gcp/vertex

# Set up Python virtual environment
python -m venv venv
source venv/bin/activate

# Install required Python packages
pip install -r requirements.txt

# Define variables
PROJECT_ID="bell-canada-inc"
SHORT_PROJECT_ID="bci" # Replace with your project ID
BUCKET_NAME="${SHORT_PROJECT_ID}-ai-deployment-bootcamp-model"
MODEL_SOURCE="gs://vertex-model-garden-public-us/llama3.1"
LOCATION="us-central1"
MODEL_ID="" # Optional: Fill this if you have a specific model ID to deploy
MODEL_VERSION="" # Optional: Fill this if you have a specific model version to deploy
ENDPOINT_ID="" # Optional: Fill this if you have a known endpoint ID for testing or undeploying

# Check if the bucket exists
if ! gsutil ls -b gs://${BUCKET_NAME} &> /dev/null; then
    echo "Bucket does not exist. Creating bucket: ${BUCKET_NAME}"
    gcloud storage buckets create gs://${BUCKET_NAME} --location=${LOCATION} --project=${PROJECT_ID}
else
    echo "Bucket already exists: ${BUCKET_NAME}"
fi

# Check if the folder exists in the bucket
if ! gsutil -q stat gs://${BUCKET_NAME}/llama-garden/**; then
    echo "Folder does not exist. Copying model to bucket: ${BUCKET_NAME}"
    gsutil -m cp -R ${MODEL_SOURCE} gs://${BUCKET_NAME}/llama-garden
else
    echo "Model folder already exists in the bucket: ${BUCKET_NAME}/llama-garden"
fi

# Step 2: Deploy the Model to an Endpoint
if [ -z "$MODEL_ID" ]; then
    ENDPOINT_ID=$(python -m deploy_llama_3_1_from_garden | grep "Endpoint ID:" | awk '{print $3}')
else
    ENDPOINT_ID=$(python -m deploy_llama_3_1_from_garden $MODEL_ID $MODEL_VERSION | grep "Endpoint ID:" | awk '{print $3}')
fi

echo "Deployed Endpoint ID: $ENDPOINT_ID"
sed -i "s/^endpoint =.*/endpoint = \"$ENDPOINT_ID\"/" reference_implementations/gcp/architectures/terraform.tfvars
# Optional: Test the Endpoint
# Uncomment the following line to test the endpoint with the known ENDPOINT_ID
python -m test_endpoint "inputs/llama3.1.json" $ENDPOINT_ID

# Optional: Undeploy
# Uncomment and set the ENDPOINT_ID variable if you wish to undeploy
# python -m undeploy $ENDPOINT_ID
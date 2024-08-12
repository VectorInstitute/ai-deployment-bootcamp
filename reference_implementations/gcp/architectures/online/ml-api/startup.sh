#!/bin/bash
sudo apt update -y
sudo apt install python3.8-venv libpq-dev unzip -y

export INSTANCE_NAME=`hostname`
export ZONE=$(gcloud compute instances list --filter="name=('`hostname`')" --format 'csv[no-heading](zone)')
export PROJECT_ID=$(curl http://metadata.google.internal/computeMetadata/v1/project/project-id -H Metadata-Flavor:Google)
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
export ENDPOINT_ID=$(gcloud compute instances describe $INSTANCE_NAME --format='value[](metadata.items.endpoint)' --zone=$ZONE)
export MODEL_NAME=$(gcloud compute instances describe $INSTANCE_NAME --format='value[](metadata.items.model)' --zone=$ZONE)

gcloud storage cp "gs://${PROJECT_ID}-api-source/ml-api.zip" ./
unzip ml-api.zip -d ./ml-api
cd ml-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

sudo ufw allow 8080/tcp
fastapi run main.py --port 8080 >> ml-api.log 2>&1 &

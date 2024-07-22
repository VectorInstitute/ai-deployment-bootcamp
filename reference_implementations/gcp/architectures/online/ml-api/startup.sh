#!/bin/bash
sudo apt update -y
sudo apt install python3.8-venv libpq-dev unzip -y
export ENDPOINT_ID=$(gcloud compute instances describe ml-api-vm --format='value[](metadata.items.endpoint)' --zone=us-west2-a)
gcloud storage cp gs://ai-deployment-bootcamp-api-source/ml-api.zip ./
unzip ml-api.zip -d ./ml-api
cd ml-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo ufw allow 8080/tcp
fastapi run main.py --port 8080 >> ml-api.log 2>&1 &

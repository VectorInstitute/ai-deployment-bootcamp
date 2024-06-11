#!/bin/bash
sudo apt update -y
sudo apt install python3.8-venv libpq-dev -y
git clone https://lotif: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@github.com/VectorInstitute/ai-deployment-bootcamp.git
cd ai-deployment-bootcamp
git checkout first-ideas
cd reference_implementations/gcp/step2/ml-api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
sudo ufw allow 8080/tcp
fastapi run main.py --port 8080 >> ml-api.log 2>&1 &

# Vertex

Configure docker on google cloud:
```shell
gcloud artifacts repositories create ai-deployment-bootcamp-docker-repo --repository-format docker --location us-west2
gcloud auth configure-docker us-west2-docker.pkg.dev
```

CD into `vertex/`, make a venv and install dependencies. 

Then run `build_and_push_image.py` (will take a while to finish and required docker to be running):
```shell
python -m build_and_push_image
```

***NOTE:*** Alternatively, if the image is already built, you can just push it with:
```shell
docker push us-west2-docker.pkg.dev/ai-deployment-bootcamp/ai-deployment-bootcamp-docker-repo/ai-deployment-bootcamp-inferencer:latest
```

Pull the model from huggingface (will take some time):
```shell
brew install git-lfs  # or download from https://git-lfs.com/
git lfs install
git clone https://huggingface.co/facebook/bart-large-mnli
```

Compress the model:
```shell
cd bart-large-mnli/
tar zcvf model.tar.gz --exclude flax_model.msgpack --exclude pytorch_model.bin --exclude rust_model.ot *
```

Upload model to google cloud storage:
```shell
gcloud config set storage/parallel_composite_upload_enabled True
gcloud storage cp model.tar.gz gs://ai-deployment-bootcamp
```

Make sure you're logged in, then deploy the model and create an endpoint (will take some time):
```shell
python -m deploy
```
Alternatively, you can pass in the model id and version if it has already been deployed:
```shell
python -m deploy 1562581944930140160 1
```

It will automatically update the endpoint ID in the `../terraform.tfvars` file.

# Terraform

From inside the folder with the terraform files:
```shell
terraform init -var-file=../terraform.tfvars
terraform plan -var-file=../terraform.tfvars
terraform apply -var-file=../terraform.tfvars
```

It will output the public ip address and also the SSH command. 

# FastAPI

To check the system logs, ssh into the machine and run:
```shell
tail -f /var/log/syslog
```

To check FastAPI logs, run:
```shell
tail -f /ml-api/ml-api.log
```

Once `ml-api` instance is up and FastAPI is running, the endpoint will be available at port 8080.

# Feature Store

Add some data points to the SQL database, use the `add_data_point` script:
```shell
python -m add_data_point "test data point 1"
python -m add_data_point "test data point 2"
python -m add_data_point "test data point 3"
```

To import those data points into the feature store:
```shell
python -m import_data
```

Now the data is ready to be pulled for prediction.

# Predict

To run a prediction in a data point, call the `/predict` endpoint with the data point id:
```shell
http://<instance-ip>:8080/predict/1
```

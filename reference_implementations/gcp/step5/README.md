# Vertex

Configure docker on google cloud:
```shell
gcloud artifacts repositories create ai-deployment-bootcamp-docker-repo --repository-format docker --location us-west2
gcloud auth configure-docker us-west2-docker.pkg.dev
```

CD into `vertex/`, make a venv and install dependencies. 

Then run `push_image.py` (will take a while to finish and required docker to be running):
```shell
python -m push_image
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

It will output the endpoint resource name at the end. Get the endpoint ID from it and set it to the
`ENDPOINT_ID` variable in `ml-api/main.py`.

# Terraform

From inside the folder with the terraform files:
```shell
terraform init
terraform plan
terraform apply
```

It will output the public ip address and also the SSH command. 

# FastAPI

To check the system logs, ssh into the machine and run:
```shell
tail -f /var/log/syslog
```

To check FastAPI logs, run:
```shell
tail -f /ai-deployment-bootcamp/reference_implementations/gcp/step5/ml-api/ml-api.log
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

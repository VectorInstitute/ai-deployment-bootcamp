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

It will output the endpoint resource name at the end. Get the endpoint ID from it and set it to the
`endpoint` variable in `terraform.tfvars`.

# Terraform

From inside the folder with the terraform files:
```shell
terraform init
terraform plan
terraform apply
```

It will build the rest of the pipeline based on the configuration in the terraform file.

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

You should see the ids for the data points that have been added. Now the data is ready to be pulled for prediction.

# Predict

To publish a message to the prediction queue for a data point, use the `publish.py` script:
```shell
python -m publish "{\"id\": \"1\"}"
```

The prediction should be added to the database once it has been processed.

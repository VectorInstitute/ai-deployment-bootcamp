# Uploading and Deploying a Model From Local Machine

In this example, we will checkout a model from Huggingface (namely
[bart-large-mnli](https://huggingface.co/facebook/bart-large-mnli)), package it, build a docker container
for it and deploy it to an endpoint.

You can deploy your custom model instead of the one in this example. Please change the steps below
and most crucially the predictor code to match your custom model. 

***NOTE:*** while you run the scripts below for the first time, the CLI will output errors asking to enable
the APIs you are using for the first time. It will also be kind enough to let you know the URLs you
need to access in order to do so. Please enable the APIs as needed while running this for the
first time.

### 1. Package the Model and Build the Docker Container

First, on some location in your machine, clone the `bart-large-mnli` repo which contains
the model from huggingface (it will take some time to download it):
```shell
git clone https://huggingface.co/facebook/bart-large-mnli
```

The model predictor at [vertex/predictor/hf_predictor.py](vertex/predictor/hf_predictor.py)
expects all model files to be in a `.tar.gz` package so it can unpack and build a prediction
pipeline for it at load time. To make the package, run:
```shell
cd bart-large-mnli/
tar zcvf model.tar.gz --exclude flax_model.msgpack --exclude pytorch_model.bin --exclude rust_model.ot *
```

Create a bucket on Cloud Storage and upload the compressed model to it (make sure to match
the project ID and region to the ones you have set up on the [`terraform.tfvars`](architectures/terraform.tfvars)
file). Make sure to choose a unique bucket name:
```shell
gcloud storage buckets create gs://ai-deployment-bootcamp-model --location=us-central1 --project=ai-deployment-bootcamp
gcloud config set storage/parallel_composite_upload_enabled True
gcloud storage cp model.tar.gz gs://ai-deployment-bootcamp-model/model/
```

Configure docker on GCP with the commands below (make sure to match the project ID and region to
the ones you have set up on the [`terraform.tfvars`](architectures/terraform.tfvars) file):
```shell
gcloud artifacts repositories create ai-deployment-bootcamp-docker-repo --repository-format docker --location us-central1 --project ai-deployment-bootcamp
gcloud auth configure-docker us-central1-docker.pkg.dev
```

Then, back on `/vertex`, run `build_and_push_image.py` (it will take a while to finish and requires
Docker to be running). This will build a Docker image with the [vertex/predictor/hf_predictor.py](vertex/predictor/hf_predictor.py)
file as the predictor code for the model. This Docker image will be specifically built to run on
a Vertex AI endpoint, which we will create on the next step.
```shell
python -m build_and_push_image
```

***NOTE 1:*** There is a weird bug with docker credentials. If you see the error below,
try this fix: https://stackoverflow.com/questions/65896681/exec-docker-credential-desktop-exe-executable-file-not-found-in-path
```shell
INFO: #3 ERROR: error getting credentials - err: exec: "docker-credential-desktop": executable file not found in $PATH, out: ``
```

***NOTE 2:*** Alternatively, if the image is already built, you can just push it with:
```shell
docker push us-central1-docker.pkg.dev/ai-deployment-bootcamp/ai-deployment-bootcamp-docker-repo/ai-deployment-bootcamp-inferencer:latest
```

### 2. Deploy the Model to an Endpoint

Deploy the model and create an endpoint by running the command below (will take some
time to finish):
```shell
python -m deploy
```
Alternatively, if you already have deployed a model to the registry before, you can pass
in the model ID and version (optional) to the script so it can deploy it to the endpoint:
```shell
python -m deploy 1562581944930140160 1
```

At the end, it will output the endpoint ID. It will automatically update the endpoint ID
and the model name in the `architectures/terraform.tfvars` file so the rest of the
pipeline can use it.

To test if the endpoint is up and running, run the test script with the test input data
for this model and the endpoint ID:
```shell
python -m test_endpoint "inputs/bart-mnli.json" 4843021065888202752
```

## Update the Model Version

If a new version of the model has been trained, you can update it by running the
`update_model_version.py` script.

Assuming the Docker container with the predictor stays the same and the new model
version has already been uploaded to cloud storage, you can call the script passing
in the ID of the parent model (e.g. the model you want to "replace" with this new
version) and the path for the new model version in cloud storage:
```shell
python -m update_model_version 1562581944930140160 gs://ai-deployment-bootcamp-model/model_v2/
```

The script will:
- Upload the new model from cloud storage to Vertex AI, creating a new version
under the parent model and setting the new version as the default
- Deploy the new model version to the endpoint ID configured in the
[`terraform.tfvars`](architectures/terraform.tfvars) file.
- Once the new model version has been deployed successfully to the endpoint,
it will undeploy all the other models deployed to that endpoint 

## Undeploy

When you're done using the model, run the `undeploy.py` script to remove the model from
the endpoint and delete the endpoint. You can call it passing the endpoint ID as
a parameter:
```shell
python -m undeploy 4843021065888202752
```

***NOTE:*** This will not delete the model from the model registry or from cloud
storage as the costs to keep those are really small.

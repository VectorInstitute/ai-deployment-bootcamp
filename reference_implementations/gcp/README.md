# GCP Reference Implementations

## Set Up

To run the GCP reference implementations, you must first install:
- [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- [Terraform](https://developer.hashicorp.com/terraform/install)
- [Python](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/engine/install/)
- [Git LFS](https://git-lfs.com/)
    - Make sure to install it into your local git by running `git lfs install`

Set your user name and project name variables on the [`architectures/terraform.tfvars`](architectures/terraform.tfvars)
file. For this example, the project name will be `ai-deployment-bootcamp`.

Make sure you have an account with GCP and are authenticated in the CLI by running:
```shell
gcloud init
gcloud auth login
gcloud auth application-default login
gcloud config set project ai-deployment-bootcamp
```

Next, go into the `vertex` folder, create a virtual environment and install the project requirements:
```shell
cd vertex
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You should also make a public-private key pair:
- On Windows, use [this guide](https://www.purdue.edu/science/scienceit/ssh-keys-windows.html).
- On Max and Linux, use [this guide](https://mdl.library.utoronto.ca/technology/tutorials/generating-ssh-key-pairs-mac).

Set the value of the `publickeypath` variable in the [`architectures/terraform.tfvars`](architectures/terraform.tfvars)
file to the path of the public key that has just been created.

## Build and deploy the model

First, while you run the scripts below for the first time, the CLI will output errors asking to enable
the APIs you are using for the first time. It will also be kind enough to let you know the URLs you
need to access in order to do so. Please enable the APIs as needed while running this for the
first time.

Second, if you are using the model from this reference implementation, just follow the instructions below.
For your own model, you can customize the instructions as needed

### 1. Build

First, one some other location in your machine, clone the `bart-large-mnli` repo which contains
the model from huggingface (it will take some time to download it):
```shell
git clone https://huggingface.co/facebook/bart-large-mnli
```

Then, compress the model:
```shell
cd bart-large-mnli/
tar zcvf model.tar.gz --exclude flax_model.msgpack --exclude pytorch_model.bin --exclude rust_model.ot *
```

Create a bucket and upload the compressed model to it (make sure to match the project ID and
region to the ones you have set up on the `terraform.tfvars` file). Make sure to choose an
unique bucket name:
```shell
gcloud storage buckets create gs://ai-deployment-bootcamp-model --location=us-central1 --project=ai-deployment-bootcamp
gcloud config set storage/parallel_composite_upload_enabled True
gcloud storage cp model.tar.gz gs://ai-deployment-bootcamp-model/model/
```

Configure docker on GCP with the commands below (make sure to match the project
ID and region to the ones you have set up on the [`terraform.tfvars`](architectures/terraform.tfvars)
file):
```shell
gcloud artifacts repositories create ai-deployment-bootcamp-docker-repo --repository-format docker --location us-central1 --project ai-deployment-bootcamp
gcloud auth configure-docker us-central1-docker.pkg.dev
```

Then, back on `/vertex`, run `build_and_push_image.py` (it will take a while to finish and requires
docker to be running):
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

### 2. Deploy

Deploy the model and create an endpoint by running the command below (will take some
time to deploy the model to the endpoint):
```shell
python -m deploy
```
Alternatively, if you already have deployed a model before, you can pass in the model
id and version to the script:
```shell
python -m deploy 1562581944930140160 1
```

It will automatically update the endpoint ID in the `architectures/terraform.tfvars` file.

To test if the endpoint is up and running, run the test script with some input data:
```shell
python -m test_endpoint "test input data"
```

## Make the Inferencing Architecture

From here you have two choices:
- If you need an online (real-time) inferencing architecture, please follow the
[architectures/online/README.md](architectures/online/README.md) guide.
- If you need an offline (batch) inferencing architecture, please follow the
[architectures/offline/README.md](architectures/offline/README.md) guide.

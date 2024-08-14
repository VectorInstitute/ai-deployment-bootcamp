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

## Build the Model Container and Deploy It

We have come up with 2 examples for deploying models, please choose the most appropriate for your use case:
1. **[Uploading a model from your local machine](upload_model_from_local.md)**: in this example, we will package
a model stored in the local machine, upload it to Cloud Storage and build a Docker image to provide inferences
from it. The model used in this example is
[bart-large-mnli from Huggingface](https://huggingface.co/facebook/bart-large-mnli).
2. **[Loading a model from Model Garden](use_model_from_garden.md)**: in this example, we pick a model from
[Vertex AI's Model Garden](https://console.cloud.google.com/vertex-ai/model-garden) and deploy it according
to its instructions. The model used in this example is
[Meta's Llama 3.1](https://console.cloud.google.com/vertex-ai/publishers/meta/model-garden/llama3_1).

## Make the Inferencing Architecture

From here you have two choices:
- If you need an online (real-time) inferencing architecture, please follow the
[architectures/online/README.md](architectures/online/README.md) guide.
- If you need an offline (batch) inferencing architecture, please follow the
[architectures/offline/README.md](architectures/offline/README.md) guide.

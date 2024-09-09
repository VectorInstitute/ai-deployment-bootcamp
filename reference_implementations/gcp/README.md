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

## Working with Datasets

We provide one sample dataset to be used as a test (`CNN_DailyMail`, details below), but feel free to
change the code and experiment with other datasets as needed.

The [CNN_DailyMail](../../data/CNN_DailyMail) dataset is a machine summarization dataset containing
news articles and a summary of each one of them. We have built a summarization predictor using
[Llama 3.1 from Model Garden](use_model_from_garden.md), here is how to use it.

First, make sure you deploy the model and the endpoint is working by calling the script below
with the endpoint id:
```shell
python -m test_endpoint inputs/llama3.1_summarization.json 6728657119244976128
```

In the output text from the model that the script prints, there should be a section stating the
text below, followed by the summary:
```text
\\nOutput:\\nHere is a summary of the text in under 100 words:
```

Next, make sure you have followed one of the guides under 
[Make the Inferencing Architecture](#make-the-inferencing-architecture) and have a pipeline
up and running. Then, let's import the dataset to the DB so the data can be used by the pipeline:
```shell
python -m import_dataset_to_db --datasetname CNN_DailyMail_sample
```

Here we are using a sample of the dataset, but you can import the whole dataset if you wish.

Next, import the data from the DB into the Feature Store:
```shell
python -m import_data_to_fs
```

Now the data is ready to be inferenced on. There is a `task` parameter in the APIs to trigger
the summarization prompt template, so you just need to pass in that parameter with value
`summarization` to indicate you want a summarization of the input data (instead of text
generation).

For the online pipeline, you can run:
```shell
http://<instance-ip>:8080/predict/1?task=summarization
```
For the offline pipeline, you can run:
```shell
python -m publish "{\"id\": \"1\",\"task\":\"summarization\"}"
```

If you're just running tests and experiments, don't forget to destroy all terraform
resources and undeploy the model endpoint once you're done.

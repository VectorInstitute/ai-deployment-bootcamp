# GCP Reference Implementations

## Set Up

To run the GCP reference implementations, you must first install:
- [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- [Terraform](https://developer.hashicorp.com/terraform/install)
- [Python](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/engine/install/)

Make sure you have created an account with GCP and are authenticated in the CLI by running:
```shell
gcloud init
gcloud auth login
```

Also, add your user to the `user` variable on the [`terraform.tfvars`](architectures/terraform.tfvars)
file. Feel free to change any of those variables as you see fit.

Next, CD into the `vertex` folder, create a virtual environment and install the project requirements:
```shell
cd vertex
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Build and deploy the model

If you are using the model we are using for this reference implementation, just follow the instructions below.
For your own model, you can customize the instructions as needed

Configure docker on GCP with the commands below (make sure to match the project
ID and region to the ones you have set up on the [`terraform.tfvars`](architectures/terraform.tfvars) file):
```shell
gcloud artifacts repositories create ai-deployment-bootcamp-docker-repo --repository-format docker --location us-west2
gcloud auth configure-docker us-west2-docker.pkg.dev
```

Then run `build_and_push_image.py` (it will take a while to finish and required docker to be running):
```shell
python -m build_and_push_image
```

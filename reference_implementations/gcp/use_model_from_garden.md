# Deploying a Model From the Model Garden

In this example, we will pick a model from [Vertex AI's Model Garden](https://console.cloud.google.com/vertex-ai/model-garden)
(namely [Meta's Llama 3.1](https://console.cloud.google.com/vertex-ai/publishers/meta/model-garden/llama3_1))
and deploy it according to its instructions.

Each model in the Model Garden has its own specific way to be deployed. If you wish to use a different
model from there, make sure follow the instructions in the model card to make sure it will work
as intended.

***NOTE:*** while you run the scripts below for the first time, the CLI will output errors asking to enable
the APIs you are using for the first time. It will also be kind enough to let you know the URLs you
need to access in order to do so. Please enable the APIs as needed while running this for the
first time.

### 1. Copy the Model to Cloud Storage

Create a bucket and copy the model files from the shared location to your Cloud Storage (make sure to match
the project ID and region to the ones you have set up on the [`terraform.tfvars`](architectures/terraform.tfvars)
file):
```shell
gcloud storage buckets create gs://ai-deployment-bootcamp-model --location=us-central1 --project=ai-deployment-bootcamp
gsutil -m cp -R gs://vertex-model-garden-public-us/llama3.1 gs://ai-deployment-bootcamp-model/llama-garden
```

We will use a pre-build Docker image to run the model so there is no need to build one.

### 2. Deploy the Model to an Endpoint

Deploy the model and create an endpoint by running the command below (will take some
time to finish):
```shell
python -m deploy_llama_3_1_from_garden
```

Alternatively, if you already have deployed a model to the registry before, you can pass
in the model ID and version (optional) to the script so it can deploy it to the endpoint:
```shell
python -m deploy_llama_3_1_from_garden 1562581944930140160 1
```

At the end, it will output the endpoint ID. It will automatically update the endpoint ID
and the model name in the `architectures/terraform.tfvars` file so the rest of the
pipeline can use it.

To test if the endpoint is up and running, run the test script with the test input data
for this model and the endpoint ID:
```shell
python -m test_endpoint "inputs/llama3.1.json" 4843021065888202752
```

## Undeploy

When you're done using the model, run the `undeploy.py` script to remove the model from
the endpoint and delete the endpoint. You can call it passing the endpoint ID as
a parameter:
```shell
python -m undeploy 4843021065888202752
```

***NOTE:*** This will not delete the model from the model registry or from cloud
storage as the costs to keep those are really small.

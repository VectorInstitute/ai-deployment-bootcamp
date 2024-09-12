project = "ai-deployment-bootcamp"
region = "us-east-1"
prefix = "poc"
infra_env = "dev"
contact = "test@test.com"
default_profile = "sagemaker"
sagemaker_endpoint_conf_name = "paraphrase-bert-en-conf-tf"
sagemaker_endpoint_conf_variant_name = "paraphrase-bert-en-conf"
sagemaker_endpoint_name = "paraphrase-bert-en-endpoint"
sagemaker_model_name = "paraphrase-bert-en-tf"
sagemaker_model_instance_count = 1
sagemaker_model_instance_type = "ml.inf1.xlarge"
sagemaker_model_mode = "SingleModel"
sagemaker_container_repo_url = "763104351884.dkr.ecr.us-east-1.amazonaws.com/pytorch-inference:1.9.0-cpu-py38-ubuntu20.04"
# sagemaker_container_repo_url = "public.ecr.aws/neuron/pytorch-inference-neuronx:2.1.2-neuronx-py310-sdk2.19.1-ubuntu20.04"
# 763104351884.dkr.ecr.<region>.amazonaws.com/pytorch-inference:<version>-inf1

# TODO: change to s3 url after model was compiled and uploaded
sagemaker_model_data_s3_url = "s3://sagemaker-us-east-1-025066243062/bert-seq-classification/traced_model.tar.gz"
rest_api_name = "paraphrase-bert-rest-api"
rest_api_description = "API for paraphrase-bert-en"
master_username = "admin"
master_password = "0jwetQ1xz7$"
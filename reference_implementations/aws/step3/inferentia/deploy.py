import boto3
import sagemaker
from sagemaker.huggingface import HuggingFaceModel
from sagemaker.predictor import Predictor
from datetime import datetime
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer

prefix = "paraphrase-bert-en"
hardware="inf1"
date_string = datetime.now().strftime("%Y%m-%d%H-%M%S")
compilation_job_name = f"paraphrase-bert-en-{hardware}-" + date_string

sagemaker_session = sagemaker.Session()
sess_bucket = sagemaker_session.default_bucket()
print(f"{sess_bucket=}")
output_model_path = f"s3://{sess_bucket}/{prefix}/{hardware}-model/"

try:
	role = sagemaker.get_execution_role()
except ValueError:
	iam = boto3.client('iam')
	role = iam.get_role(RoleName='sagemaker_execution_role')['Role']['Arn']

print(f"Role: \n{role=}")

model_s3_url = f"s3://sagemaker-us-east-1-025066243062/bert-seq-classification/traced-model/traced_model.tar.gz"


# versions are found in model's HF page
hf_model  = HuggingFaceModel(
    model_data=model_s3_url,
    predictor_cls=Predictor,
    transformers_version="4.12.3",
    pytorch_version='1.9',
    role=role,
    source_dir="code",
    entry_point="inference.py",
    py_version="py39",
    name=f"distilbert-{date_string}",
    env={"SAGEMAKER_CONTAINER_LOG_LEVEL": "10"},
)


import json

import boto3
import botocore

s3 = boto3.resource('s3')

try:
    s3.Object('sagemaker-us-east-1-025066243062', "neuron-experiments/bert-seq-classification/traced-model/traced_model.tar.gz").load()
except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == "404":
        print("doesnot exit")
    else:
        print("someting went wrong")
        raise
else:
    print("# The object does exist.")

s3 = boto3.client('s3')
    
    # List objects with the specific prefix (folder)
result = s3.list_objects_v2(Bucket="sagemaker-us-east-1-025066243062",
                            Prefix="neuron-experiments/bert-seq-classification/")

print(f"{result=}")

print(f"{output_model_path=}")

print("HF Model created. Proceeding to compilation...")

compiled_model = hf_model.compile(
    target_instance_family=f"ml_{hardware}",
    input_shape={"input_ids": [1, 512], "attention_mask": [1, 512]},
    output_path=output_model_path,
    job_name=f"compilation-job-{date_string}",
    framework="pytorch",
    framework_version="1.9",
	role=role,
    compiler_options=json.dumps("--dtype int64"),
    compile_max_run=900,
)

print("Compilation job name: {} \nOutput model path in S3: {}".format(compilation_job_name, output_model_path))

compiled_inf1_predictor = compiled_model.deploy(
    instance_type="ml.inf1.xlarge",
    initial_instance_count=1,
    endpoint_name=f"paraphrase-bert-en-{hardware}-{date_string}",
    serializer=JSONSerializer(),
    deserializer=JSONDeserializer(),
    wait=False
)

print(f"Model deployed: {compiled_inf1_predictor.endpoint_name}")

# Perform test inference

# # Predict with model endpoint
# client = boto3.client('sagemaker')

# #let's make sure it is up und running first
# status = ""
# while status != 'InService':
#     endpoint_response = client.describe_endpoint(EndpointName=f"paraphrase-bert-en-{hardware}-{date_string}")
#     status = endpoint_response['EndpointStatus']


# # Send a payload to the endpoint and recieve the inference
# seq_0 = "Welcome to Vector AI Deployment Bootcamp! Thank you for attending the workshop on deploying ML models on Inferentia instances."
# seq_1 = seq_0
# payload = seq_0, seq_1
# compiled_inf1_predictor.predict(payload)

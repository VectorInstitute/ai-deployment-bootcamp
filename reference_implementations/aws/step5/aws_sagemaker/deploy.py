import boto3
import json
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

# This is the bucket that we uploaded model's artifacts to
sess_bucket = sagemaker_session.default_bucket()
print(f"{sess_bucket=}")

output_model_path = f"s3://{sess_bucket}/{prefix}/{hardware}-model/"

try:
	role = sagemaker.get_execution_role()
except ValueError:
	iam = boto3.client('iam')
	role = iam.get_role(RoleName='sagemaker_execution_role')['Role']['Arn']

print(f"Role: \n{role=}")

# TODO: Replace with the path to your traced model artifact for compilation
model_s3_url = f"s3://sagemaker-us-east-1-025066243062/bert-seq-classification/traced_model.tar.gz"


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


print("HF Model created. Proceeding to compilation...")

# Models need to be compiled for Inferentia chips
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

# TODO: Pro-tip - look into other parameters of deploy to know more about different endpoint types
compiled_inf1_predictor = compiled_model.deploy(
    instance_type="ml.inf1.xlarge",
    initial_instance_count=1,
    endpoint_name=f"paraphrase-bert-en-{hardware}-{date_string}",
    serializer=JSONSerializer(),
    deserializer=JSONDeserializer(),
    wait=False
)

print(f"Model deployed: {compiled_inf1_predictor.endpoint_name}")

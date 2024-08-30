from sagemaker.huggingface import HuggingFaceModel
from sagemaker.predictor import Predictor
from datetime import datetime
import sagemaker
import boto3
from sagemaker.serializers import JSONSerializer
from sagemaker.deserializers import JSONDeserializer

prefix = "neuron-experiments/bert-seq-classification"
flavour = "normal"
date_string = datetime.now().strftime("%Y%m-%d%H-%M%S")

normal_model_url = f"s3://sagemaker-us-east-1-025066243062/bert-seq-classification/normal-model/normal_model.tar.gz"

try:
	role = sagemaker.get_execution_role()
except ValueError:
	iam = boto3.client('iam')
	role = iam.get_role(RoleName='sagemaker_execution_role')['Role']['Arn']

normal_sm_model = HuggingFaceModel(
    model_data=normal_model_url,
    predictor_cls=Predictor,
    transformers_version="4.12.3",
    pytorch_version='1.9.1',
    role=role,
	source_dir="code",
    entry_point="inference.py",
    py_version="py38",
    name=f"{flavour}-distilbert-{date_string}",
    env={"SAGEMAKER_CONTAINER_LOG_LEVEL": "10"},
)


hardware = "g4dn"

normal_predictor = normal_sm_model.deploy(
    instance_type="ml.g4dn.xlarge",
    initial_instance_count=1,
    endpoint_name=f"paraphrase-bert-en-{hardware}-{date_string}",
    serializer=JSONSerializer(),
    deserializer=JSONDeserializer(),
)
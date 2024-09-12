from sagemaker.utils import load_tfvars


TFVARS_PATH = "terraform.tfvars"
TFVARS = load_tfvars(TFVARS_PATH)

MODEL_NAME = "paraphrase-bert"

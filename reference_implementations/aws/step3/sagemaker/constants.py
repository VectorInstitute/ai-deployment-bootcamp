from utils import load_tfvars, get_project_number


TFVARS_PATH = "../architectures/terraform.tfvars"
TFVARS = load_tfvars(TFVARS_PATH)

PROJECT_NUMBER = get_project_number(TFVARS["project"])
MODEL_NAME = "bart-large-mnli"
DOCKER_REPO_NAME = f"{TFVARS['project']}-docker-repo"
DOCKER_IMAGE_NAME = f"{TFVARS['project']}-inferencer"
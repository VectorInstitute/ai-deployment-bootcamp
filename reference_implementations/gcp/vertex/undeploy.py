import sys

from google.cloud import aiplatform

from utils import load_tfvars, get_project_number

# Load TF Vars
TFVARS_PATH = "../architectures/terraform.tfvars"
tfvars = load_tfvars(TFVARS_PATH)
project_number = get_project_number(tfvars["project"])

aiplatform.init(project=tfvars["project"], location=tfvars["region"])

endpoint = aiplatform.models.Endpoint(
    endpoint_name=f"projects/{project_number}/locations/{tfvars['region']}/endpoints/{tfvars['endpoint']}",
)

endpoint.undeploy_all()
endpoint.delete()

import sys

from google.cloud import aiplatform

from constants import TFVARS, PROJECT_NUMBER


endpoint = sys.argv[1] if len(sys.argv) >= 2 else TFVARS['endpoint']

aiplatform.init(project=TFVARS["project"], location=TFVARS["region"])

endpoint = aiplatform.models.Endpoint(
    endpoint_name=f"projects/{PROJECT_NUMBER}/locations/{TFVARS['region']}/endpoints/{endpoint}",
)

endpoint.undeploy_all()
endpoint.delete()

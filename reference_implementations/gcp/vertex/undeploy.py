from google.cloud import aiplatform

from constants import TFVARS, PROJECT_NUMBER


aiplatform.init(project=TFVARS["project"], location=TFVARS["region"])

endpoint = aiplatform.models.Endpoint(
    endpoint_name=f"projects/{PROJECT_NUMBER}/locations/{TFVARS['region']}/endpoints/{TFVARS['endpoint']}",
)

endpoint.undeploy_all()
endpoint.delete()

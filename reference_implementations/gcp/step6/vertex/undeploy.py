import sys

from google.cloud import aiplatform

endpoint_id = sys.argv[1] if len(sys.argv) > 1 else None

aiplatform.init(project="ai-deployment-bootcamp", location="us-west2")

endpoint = aiplatform.models.Endpoint(
    endpoint_name=f"projects/761003357790/locations/us-west2/endpoints/{endpoint_id}",
)

endpoint.undeploy_all()
endpoint.delete()

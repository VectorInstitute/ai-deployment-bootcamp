import logging
import sys

from google.cloud import aiplatform

from constants import TFVARS, TFVARS_PATH, PROJECT_NUMBER
from utils import create_service_account_with_roles, save_tfvars

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s")

aiplatform.init(project=TFVARS["project"], location=TFVARS["region"])

model_id = sys.argv[1] if len(sys.argv) > 1 else None
model_version = sys.argv[2] if len(sys.argv) > 2 else "default"

model_name = "llama-from-garden"

if model_id is not None:
    model = aiplatform.Model(f"projects/{PROJECT_NUMBER}/locations/{TFVARS['region']}/models/{model_id}@{model_version}")
else:
    model_path = f"gs://{TFVARS['project']}-model/llama-garden/llama3.1/Meta-Llama-3.1-8B"
    vllm_args = [
        "python",
        "-m",
        "vllm.entrypoints.api_server",
        "--host=0.0.0.0",
        "--port=7080",
        f"--model={model_path}",
        f"--tensor-parallel-size=1",
        "--swap-space=16",
        f"--gpu-memory-utilization=0.9",
        f"--max-model-len=8192",
        "--enable-lora",
        "--disable-custom-all-reduce",
        f"--max-loras=1",
        f"--max-cpu-loras=16",
        "--disable-log-stats",
    ]

    env_vars = {"MODEL_ID": model_path, "DEPLOY_SOURCE": "notebook"}
    model = aiplatform.Model.upload(
        display_name=model_name,
        serving_container_image_uri="us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:20240726_1329_RC00",
        serving_container_args=vllm_args,
        serving_container_ports=[7080],
        serving_container_predict_route="/generate",
        serving_container_health_route="/ping",
        serving_container_environment_variables=env_vars,
    )

service_account = create_service_account_with_roles(
    account_id=f"{TFVARS['short_project_prefix']}-llama-sa",
    account_display_name=f"{TFVARS['project']} Llama Endpoint Service Account",
    project_id=TFVARS["project"],
    roles=["roles/aiplatform.user", "roles/storage.objectViewer"],
)

endpoint = aiplatform.Endpoint.create(display_name=f"{TFVARS['project']}-llama-garden-endpoint")

# Saving the endpoint id in the tfvars
TFVARS["endpoint"] = endpoint.name
save_tfvars(TFVARS, TFVARS_PATH)

model.deploy(
    endpoint=endpoint,
    machine_type="g2-standard-8",
    accelerator_type="NVIDIA_L4",
    accelerator_count=1,
    deploy_request_timeout=1800,
    service_account=service_account.email,
)
print("Endpoint ID:", endpoint.name)

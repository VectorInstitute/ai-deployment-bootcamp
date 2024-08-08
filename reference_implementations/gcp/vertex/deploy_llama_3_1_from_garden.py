import logging

from google.cloud import aiplatform

from constants import TFVARS

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s")

model_id = "gs://ai-deployment-bootcamp-430513-model/llama-garden/llama3.1/Meta-Llama-3.1-8B"

aiplatform.init(project=TFVARS["project"], location=TFVARS["region"])

endpoint = aiplatform.Endpoint.create(display_name=f"{TFVARS['project']}-llama-garden-endpoint")

vllm_args = [
    "python",
    "-m",
    "vllm.entrypoints.api_server",
    "--host=0.0.0.0",
    "--port=7080",
    f"--model={model_id}",
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

env_vars = {"MODEL_ID": model_id, "DEPLOY_SOURCE": "notebook"}
model = aiplatform.Model.upload(
    display_name="llama-from-garden",
    serving_container_image_uri="us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:20240726_1329_RC00",
    serving_container_args=vllm_args,
    serving_container_ports=[7080],
    serving_container_predict_route="/generate",
    serving_container_health_route="/ping",
    serving_container_environment_variables=env_vars,
)

model.deploy(
    endpoint=endpoint,
    machine_type="g2-standard-8",
    accelerator_type="NVIDIA_L4",
    accelerator_count=1,
    deploy_request_timeout=1800,
)
print("endpoint_name:", endpoint.name)

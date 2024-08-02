# Resource: https://www.philschmid.de/sagemaker-llm-vpc

from pathlib import Path
import os
from sagemaker.s3 import S3Uploader
 
# set HF_HUB_ENABLE_HF_TRANSFER env var to enable hf-transfer for faster downloads
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
from huggingface_hub import snapshot_download
 
HF_MODEL_ID = "facebook/bart-large-mnli"
# create model dir
model_tar_dir = Path(HF_MODEL_ID.split("/")[-1])
model_tar_dir.mkdir(exist_ok=True)
 
# Download model from Hugging Face into model_dir
snapshot_download(
    HF_MODEL_ID,
    local_dir=str(model_tar_dir), # download to model dir
    revision="main", # use a specific revision, e.g. refs/pr/21
    local_dir_use_symlinks=False, # use no symlinks to save disk space
    ignore_patterns=["*.msgpack*", "*.h5*", "*.bin*"], # to load safetensor weights
)
 
# check if safetensor weights are downloaded and available
assert len(list(model_tar_dir.glob("*.safetensors"))) > 0, "Model download failed"

# Compressing

parent_dir=os.getcwd()
# change to model dir
os.chdir(str(model_tar_dir))
# use pigz for faster and parallel compression. May need to install it using `brew install pigz`
!tar -cf model.tar.gz --use-compress-program=pigz *
# change back to parent dir
os.chdir(parent_dir)

# Upload to S3 bucket

s3_model_uri = S3Uploader.upload(
    local_path=str(model_tar_dir.joinpath("model.tar.gz")), desired_s3_uri=f"s3://{TFVAR[bucket_name]}/bart-large-mnli"
)
 
print(f"model uploaded to: {s3_model_uri}")
 
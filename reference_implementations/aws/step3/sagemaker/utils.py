from typing import Dict

import hcl2
import boto3
from pytfvars import tfvars

def get_project_number() -> str:
    client = boto3.client('sts')
    response = client.get_caller_identity()
    account_id = response['Account']
    return account_id


def load_tfvars(tfvars_path: str) -> Dict[str, str]:
    with open(tfvars_path, "r") as file:
        return hcl2.load(file)


def save_tfvars(tfvars_dict: Dict[str, str], tfvars_path: str):
    with open(tfvars_path, "w") as file:
        file.write(tfvars.convert(tfvars_dict))
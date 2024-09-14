from typing import Dict

import hcl2
from pytfvars import tfvars


def load_tfvars(tfvars_path: str) -> Dict[str, str]:
    with open(tfvars_path, "r") as file:
        return hcl2.load(file)


def save_tfvars(tfvars_dict: Dict[str, str], tfvars_path: str):
    with open(tfvars_path, "w") as file:
        file.write(tfvars.convert(tfvars_dict))

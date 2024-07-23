from typing import Dict

import hcl2
from google.cloud import resourcemanager_v3
from pytfvars import tfvars


def get_project_number(project_id: str) -> str:
    rm = resourcemanager_v3.ProjectsClient()
    req = resourcemanager_v3.GetProjectRequest(name=f"projects/{project_id}")
    res = rm.get_project(request=req)
    project_number = res.name.split("/")[1]
    return project_number


def load_tfvars(tfvars_path: str) -> Dict[str, str]:
    with open(tfvars_path, "r") as file:
        return hcl2.load(file)


def save_tfvars(tfvars_dict: Dict[str, str], tfvars_path: str):
    with open(tfvars_path, "w") as file:
        file.write(tfvars.convert(tfvars_dict))


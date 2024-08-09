from typing import Dict, List

import hcl2
from google.cloud import resourcemanager_v3, iam_admin_v1
from google.iam.v1 import iam_policy_pb2
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


def create_service_account_with_roles(
    account_id: str,
    account_display_name: str,
    project_id: str,
    roles: List[str],
) -> iam_admin_v1.types.ServiceAccount:
    iam_admin_client = iam_admin_v1.IAMClient()

    # Retrieving account if it exists
    request = iam_admin_v1.types.ListServiceAccountsRequest()
    request.name = f"projects/{project_id}"
    accounts = iam_admin_client.list_service_accounts(request=request)

    account_name = f"projects/{project_id}/serviceAccounts/{account_id}@{project_id}.iam.gserviceaccount.com"
    account = None

    for acct in accounts.accounts:
        if acct.name == account_name:
            account = acct
            print("Account exists, skipping creation.")
            break

    if account is None:
        # Creating account if it doesn't exist
        service_account = iam_admin_v1.types.ServiceAccount()
        service_account.display_name = account_display_name

        request = iam_admin_v1.types.CreateServiceAccountRequest()
        request.account_id = account_id
        request.name = f"projects/{project_id}"
        request.service_account = service_account

        account = iam_admin_client.create_service_account(request=request)

    # Getting current policy
    client = resourcemanager_v3.ProjectsClient()
    request = iam_policy_pb2.GetIamPolicyRequest()
    request.resource = f"projects/{project_id}"
    policy = client.get_iam_policy(request)

    # Add member to role if it exists, if not add a new binding
    member = f"serviceAccount:{account.email}"
    for role in roles:
        found = False
        for bind in policy.bindings:
            if bind.role == role:
                found = True
                bind.members.append(member)
                break
        if not found:
            policy["bindings"].append({"role": role, "members": [member]})

    # Saving policy
    request = iam_policy_pb2.SetIamPolicyRequest()
    request.resource = f"projects/{project_id}"
    request.policy.CopyFrom(policy)
    client.set_iam_policy(request)

    return account

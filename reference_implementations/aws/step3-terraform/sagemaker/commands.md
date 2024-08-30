## configure AWS

## Add required roles (admin)

## S3 bucket

## Terraform

## Lambda functions

## Create Role:
```bash
aws iam create-role \
    --role-name sagemaker_execution_role \
    --assume-role-policy-document file://trust-policy.json

```

## Assign policy to the role:
```bash
aws iam attach-role-policy \
    --role-name sagemaker_execution_role \
    --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

```
# Delete the endpoint
aws sagemaker delete-endpoint --endpoint-name your-endpoint-name

# Delete the model associated with the endpoint
aws sagemaker delete-model --model-name your-model-name

## Not Recommended 
Attach administrator role in the console

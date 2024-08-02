import boto3
import docker

def build_and_push(image_tag, ecr_repo):
  # Build Docker image
  client = docker.from_env()
  client.images.build(path='.', dockerfile='Dockerfile', tag=image_tag)

  # Push to ECR (replace with your ECR credentials)
  ecr_client = boto3.client('ecr')
  ecr_client.login()
  ecr_client.images.push(f"{ecr_repo}:{image_tag}")

# Example usage:
image_tag = 'my_image:latest'
ecr_repo = 'your_ecr_repository'
build_and_push(image_tag, ecr_repo)

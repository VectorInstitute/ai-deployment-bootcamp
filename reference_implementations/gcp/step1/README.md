From inside the folder with the Dockerfile:
```shell
docker build -t ai-deployment-bootcamp-step1 .
# optional:
docker run --name ai-deployment-bootcamp-step1 -d -p 8080:8080 ai-deployment-bootcamp-step1:latest
```

```shell
# One time:
gcloud artifacts repositories create ai-deployment-bootcamp-docker-repo --repository-format=docker --location=us-west2 --description="AI Deployment Bootcamp Docker repository"
# Every image change:
gcloud builds submit --region=us-west2 --tag us-west2-docker.pkg.dev/ai-deployment-bootcamp/ai-deployment-bootcamp-docker-repo/ai-deployment-bootcamp-step1:latest
```

From inside the folder with the terraform files: 
```shell
terraform init
terraform plan
terraform apply
```
From inside the folder with the terraform files:
```shell
terraform init
terraform plan
terraform apply
```

It will output the public ip address and also the SSH command.

To check the system logs, from inside the machine run:
```shell
tail -f /var/log/syslog
```

To check FastAPI logs, run:
```shell
tail -f /ai-deployment-bootcamp/reference_implementations/gcp/step2/ml-api/ml-api.log
```

Once up and running, the FastAPI endpoint will be available at:
```shell
http://<instance-ip>:8080/predict
```

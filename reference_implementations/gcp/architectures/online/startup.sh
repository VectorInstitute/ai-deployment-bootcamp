#!/bin/bash

# Initialize Terraform
echo "Initializing Terraform..."
terraform init -var-file=../terraform.tfvars

# Plan Terraform changes
echo "Planning Terraform..."
terraform plan -var-file=../terraform.tfvars

# Apply Terraform changes
echo "Applying Terraform..."
terraform apply -var-file=../terraform.tfvars -auto-approve

# Fetch the instance IP address from Terraform output
instance_ip=$(terraform output -raw public_ip_address)
echo "Instance IP: $instance_ip"

# Fetch the SSH command from Terraform output
ssh_command=$(terraform output -raw ssh_access_via_ip)
echo "SSH Command: $ssh_command"

# Wait for the ML API server to be ready
echo "Waiting for the ML API server to be ready..."
sleep 60 # Adjust the sleep time as necessary

# SSH into the machine and check the system logs
echo "Checking system logs..."
ssh -o "StrictHostKeyChecking no" $ssh_command "tail -f /var/log/syslog"

# Check the ML API logs
echo "Checking ML API logs..."
ssh -o "StrictHostKeyChecking no" $ssh_command "tail -f /ml-api/ml-api.log"

# Add a data point to the SQL database
echo "Adding a data point to the SQL database..."
python -m add_data_point "test data point 1"

# Import data points into the Feature Store
echo "Importing data points into the Feature Store..."
python -m import_data

# Run a prediction
echo "Running a prediction..."
curl "http://$instance_ip:8080/predict/1"
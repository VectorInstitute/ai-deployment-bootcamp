variable "region" {
    type = string
}
variable "project" {
    type = string
}

variable "user" {
    type = string
}

variable "scriptpath" {
    type = string
}

variable "endpoint" {
  type = string
}

variable "db_password" {
  type = string
}

variable "publickeypath" {
  type = string  
}

locals {
  redshift_port = 5439 # Change if you don't use the default port
  redshift_db_name = "databasename"
  redshift_master_user = "masteruser"
  redshift_master_password = "masterpassword"
  redshift_identifier = "my-redshift-cluster"
}

provider "redshift" {
  host     = var.redshift_host
  username = var.redshift_user
  password = var.redshift_password
}

// RedShift
resource "aws_security_group" "redshift-sg" {
  name = "redshift-sg"

  ingress {
    from_port   = local.redshift_port
    to_port     = local.redshift_port
    protocol    = "tcp"
    description = "Redshift Security Group"
    cidr_blocks = ["0.0.0.0/0"] // >
  }
}

resource "aws_redshift_cluster" "example" {
  cluster_identifier = local.redshift_identifier
  database_name      = local.redshift_db_name
  master_username    = local.redshift_master_user
  master_password    = local.redshift_master_password
  node_type          = "dc2.large"
  number_of_nodes    = 2

  vpc_security_group_ids = [aws_security_group.redshift-sg]
}


provider "aws" {
  # Configuration options
  region = "us-east-1"
}

# EC2 instance
data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

# Data source to get the default VPC ID
data "aws_vpc" "default" {
  default = true
}

resource "aws_security_group" "webserver_sg" {
  name        = "webserver-sg"
  description = "Allow HTTP traffic on port 8080"
  vpc_id      = data.aws_vpc.default.id  # Or replace with your VPC ID

  tags = {
    Name = "webserver-sg"
  }
}

resource "aws_security_group_rule" "allow_http" {
  type              = "ingress"
  from_port         = 8080
  to_port           = 8080
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.webserver_sg.id
}

resource "aws_security_group_rule" "allow_ssh" {
  type              = "ingress"
  from_port         = 22
  to_port           = 22
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.webserver_sg.id
}


output "vpc_id" {
  value = data.aws_vpc.default.id
}

output "security_group_id" {
  value = aws_security_group.webserver_sg.id
}

# SageMaker Execution Role
resource "aws_iam_role" "sagemaker_execution_role" {
  name = "sagemaker-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "sagemaker.amazonaws.com"
      }
    }]
  })
}

# Attach necessary policies to the role
resource "aws_iam_role_policy_attachment" "sagemaker_execution_policy" {
  role       = aws_iam_role.sagemaker_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSageMakerFullAccess"
}

resource "aws_instance" "ml-api-server" {
  ami           = data.aws_ami.ubuntu.id # TODO: change
  instance_type = "t3.micro"
  security_groups = [aws_security_group.webserver_sg.name]
  user_data =file(var.scriptpath)
  # You must create an SSH key pair in the AWS Management Console, 
  # AWS CLI, or AWS SDK before referencing it in the Terraform configuration.
  key_name      = var.publickeypath  # Specify your key pair name
  tags = {
    Name = "ml-api-vm"
  }
}

output "instance_public_ip" {
  value = aws_instance.ml_api_server.public_ip
}

resource "aws_sagemaker_endpoint_configuration" "ai-deployment-endpoint-config" {
  name = "ai-deployment-endpoint-config"

  # A list of ProductionVariant objects, one for each model that you want to host at this endpoint.
  production_variants {
    variant_name           = "AllTraffic"
    model_name             = aws_sagemaker_model.m.name
    initial_instance_count = 1
    instance_type          = "ml.t2.medium"
  }


  tags = {
    Name = "foo"
  }
}

resource "aws_sagemaker_endpoint" "ai-deployment-endpoint" {
  name              = "ai-deployment-endpoint"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.ai-deployment-endpoint-config.name
}

resource "aws_appautoscaling_target" "sagemaker_autoscaling_target" {
  max_capacity       = 5
  min_capacity       = 1
  resource_id        = "endpoint/ai-deployment-endpoint/variant/AllTraffic"
  scalable_dimension = "sagemaker:variant:DesiredInstanceCount"
  service_namespace  = "sagemaker"
}

resource "aws_appautoscaling_policy" "scale_up" {
  name               = "scale-up"
  resource_id        = aws_appautoscaling_target.sagemaker_autoscaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.sagemaker_autoscaling_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.sagemaker_autoscaling_target.service_namespace
  policy_type        = "TargetTrackingScaling"

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "SageMakerVariantInvocationsPerInstance"
    }

    target_value = 70.0
  }
}

resource "aws_appautoscaling_policy" "scale_down" {
  name               = "scale-down"
  resource_id        = aws_appautoscaling_target.sagemaker_autoscaling_target.resource_id
  scalable_dimension = aws_appautoscaling_target.sagemaker_autoscaling_target.scalable_dimension
  service_namespace  = aws_appautoscaling_target.sagemaker_autoscaling_target.service_namespace
  policy_type        = "TargetTrackingScaling"

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "SageMakerVariantInvocationsPerInstance"
    }

    target_value = 30.0
  }
}



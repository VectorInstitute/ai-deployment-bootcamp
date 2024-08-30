terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    region  = "us-east-1"
    bucket  = "sagemaker-endpoint-deploy-tf-state-vector"
    key     = "sagemaker-deploy/terraform.tfstate"
    profile = "sagemaker"
  }

  required_version = ">= 1.5.4"
}

data "aws_caller_identity" "current" {}

locals {
  prefix         = "${var.prefix}-${var.infra_env}"
  aws_account_id = data.aws_caller_identity.current.account_id
  common_tags = {
    Environment = var.infra_env
    Project     = var.project
    Owner       = var.contact
    ManagedBy   = "Terraform"
  }
}

# locals {
#   redshift_port = 5439 # Change if you don't use the default port
#   redshift_db_name = "databasename"
#   redshift_master_user = "masteruser"
#   redshift_master_password = "masterpassword"
#   redshift_identifier = "my-redshift-cluster"
# }

# terraform {
#   required_providers {
#     redshift = {
#       source  = "brainly/redshift"
#       version = "1.1.0"
#     }
#   }
# }

# provider "redshift" {
#   host     = var.redshift_host
#   username = var.redshift_user
#   password = var.redshift_password
# }

# // RedShift
# resource "aws_security_group" "redshift-sg" {
#   name = "redshift-sg"

#   ingress {
#     from_port   = local.redshift_port
#     to_port     = local.redshift_port
#     protocol    = "tcp"
#     description = "Redshift Security Group"
#     cidr_blocks = ["0.0.0.0/0"] // >
#   }
# }

# resource "aws_redshift_cluster" "example" {
#   cluster_identifier = local.redshift_identifier
#   database_name      = local.redshift_db_name
#   master_username    = local.redshift_master_user
#   master_password    = local.redshift_master_password
#   node_type          = "dc2.large"
#   number_of_nodes    = 2

#   vpc_security_group_ids = [aws_security_group.redshift-sg]
# }



# output "security_group_id" {
#   value = aws_security_group.webserver_sg.id
# }

# # SageMaker Execution Role
# resource "aws_iam_role" "sagemaker_execution_role" {
#   name = "sagemaker-execution-role"

#   assume_role_policy = jsonencode({
#     Version = "2012-10-17",
#     Statement = [{
#       Action = "sts:AssumeRole",
#       Effect = "Allow",
#       Principal = {
#         Service = "sagemaker.amazonaws.com"
#       }
#     }]
#   })
# }


# output "instance_public_ip" {
#   value = aws_instance.ml-api-server.public_ip
# }

# resource "aws_sagemaker_endpoint_configuration" "ai-deployment-endpoint-config" {
#   name = "ai-deployment-endpoint-config"

#   # A list of ProductionVariant objects, one for each model that you want to host at this endpoint.
#   production_variants {
#     variant_name           = "AllTraffic"
#     model_name             = aws_sagemaker_model.m.name
#     initial_instance_count = 1
#     instance_type          = "ml.t2.medium"
#   }


#   tags = {
#     Name = "foo"
#   }
# }


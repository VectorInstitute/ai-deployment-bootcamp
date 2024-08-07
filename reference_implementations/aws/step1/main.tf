variable "region" {
    type = string
}
variable "project" {
    type = string
}

variable "user" {
    type = string
}


variable "endpoint" {
  type = string
}

variable "publickeypath" {
  type = string  
}


terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "5.58.0"
    }
  }
}

provider "aws" {
  # Configuration options
  region = var.region
  profile = "default"
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

resource "aws_instance" "ml-api-server" {
  ami           = data.aws_ami.ubuntu.id # TODO: change
  instance_type = "t3.micro"
}
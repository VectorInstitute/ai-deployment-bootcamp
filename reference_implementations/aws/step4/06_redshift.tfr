# Create a VPC with a Private Subnet
resource "aws_vpc" "my_vpc" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.my_vpc.id
}

resource "aws_route_table" "public_route_table" {
  vpc_id = aws_vpc.my_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}


resource "aws_subnet" "public_subnet" {
  vpc_id            = aws_vpc.my_vpc.id
  cidr_block        = "10.0.2.0/24"
  map_public_ip_on_launch = true
}

resource "aws_route_table_association" "public_subnet_association" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_route_table.id
}

# Create a Subnet Group and Add VPC and Subnet
resource "aws_redshift_subnet_group" "redshift_subnet_group" {
  name       = "my-redshift-subnet-group"
  subnet_ids = [aws_subnet.public_subnet.id]
}

# Create a Private Amazon Redshift Cluster
resource "aws_redshift_cluster" "my_redshift_cluster" {
  cluster_identifier = "my-redshift-cluster"
  node_type          = "dc2.large"
  master_username    = "${var.master_username}"
  master_password    = "${var.master_password}"
  cluster_type       = "single-node"
  publicly_accessible = true
  skip_final_snapshot      = true
  vpc_security_group_ids = [aws_security_group.redshift_sg.id]
  cluster_subnet_group_name = aws_redshift_subnet_group.redshift_subnet_group.name
}

resource "aws_security_group" "redshift_sg" {
  vpc_id = aws_vpc.my_vpc.id

  ingress {
    from_port   = 5439
    to_port     = 5439
    protocol    = "tcp"
    # cidr_blocks = ["10.0.0.0/16"]  # Adjust for your use case - this is only from your vpc
    cidr_blocks = ["0.0.0.0/0"]  # Allow access from anywhere
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


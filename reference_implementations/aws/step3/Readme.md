## How to Create a Key Pair for AWS:

You can create a key pair using the AWS Management Console, AWS CLI, or SDK. Here is an example using the AWS CLI:

```shell
aws ec2 create-key-pair --key-name my-key-pair --query 'KeyMaterial' --output text > my-key-pair.pem
chmod 400 my-key-pair.pem

```

In this example:

    `my-key-pair` is the name of the key pair.
    `my-key-pair.pem` is the private key file that will be downloaded and used to access the instance.

## Steps to Use Your SSH Key with AWS (our approach)

### Create a Key Pair in AWS:
If you already have an SSH key pair (~/.ssh/id_rsa and ~/.ssh/id_rsa.pub), you can import the public key into AWS to create a key pair.

Use the AWS CLI to import the key:

```shell
aws ec2 import-key-pair --key-name my-key-pair --public-key-material fileb://~/.ssh/id_rsa.pub

```
`my-key-pair` is the name you want to give the key pair in AWS.
`fileb://~/.ssh/id_rsa.pub` is the local path to your public key file.

### Reference the Key Pair in Terraform:
Once the key pair is created in AWS, you can reference it by name in your Terraform configuration.
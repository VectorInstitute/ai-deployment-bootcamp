# AWS Reference Implementations

## Set Up

To run the AWS reference implementations, you must first install:
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Terraform](https://developer.hashicorp.com/terraform/install)
- [Python](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/engine/install/)
- [Git LFS](https://git-lfs.com/)
    - Make sure to install it into your local git by running `git lfs install`

## Configure

You must have an account with AWS to run this reference implementation. After you have an
account in hand, you should configure the AWS command line interface with an access key ID. 

First, you need to create an access key if you don't have one. On the
(AWS Console in your browser)[https://console.aws.amazon.com/console/home], click on the top
right menu (where your username is) and then on **Security Credentials**. Under the **Access Keys**
section, click on ***Create Access Key***. Copy the Access Key ID and Secret Access Key and store it somewhere safe, like a password manager. You won't be able to see the Secret Access Key again for this Access Key.

Now, you can start configuring the AWS CLI with the command below:
```shell
aws configure
```

 You will be asked to provide:
 - AWS Access Key ID and AWS Secret Access Key, obtained when issuing an Access Key.
 - Default region name, which can be any of the
 (regions available on AWS)[https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-regions.html].
 - Default output format, which can be set to `None`.

 After AWS CLI is configured, you can proceed to either one of the guides below,
 depending on which kind of pipeline you want to set up:
 - If you need an ***online (real-time)*** inferencing architecture, please follow the
[online/README.md](online/README.md) guide.
- If you need an ***offline (batch)*** inferencing architecture, please follow the
[offline/README.md](offline/README.md) guide.

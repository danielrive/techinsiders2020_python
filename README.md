# Tech Insiders Globant 2020

This project deploys a Python microservice in AWS ECS, using Pulumi and Python to define the infrastructure. Additionally it uses AWS Codepipeline to deploy continuously to the Production branch.

# Requirements

* **Python:** Infrastructure and microservices were built in Python. Python 3.6 or later is required.
* **AWS Account:** The Pulumi code was created to deploy resources in AWS, you need an AWS account and and an IAM user with programmatic access.
* **Pulumi Account:** You need a Pulumi account to store the state of your infrastructure and manage your project, please follow this link for more information.
https://www.Pulumi.com/docs/intro/console/accounts-and-organizations/accounts/
* **Pulumi CLI:** You need the Pulumi CLI to deploy the infrastructure changes in AWS.
https://www.Pulumi.com/docs/get-started/install/

# AWS Architecture

![aws diagram](./docs/aws_architecture.jpeg)

# Structure

The *infrastructure* folder contains the Python code used to deploy the AWS resources. This code uses Python local packages stored in the *aws_components folder*, this folder contains a package for each AWS resource required.
Pulumi uses a Python virtual environment, the file requirements.txt specifies the packages that the code will use with the virtual environment.

# Set up an environment

When you create a Pulumi account, Pulumi creates an organization by default, for a free account you can create only one organization. Each organization might have projects and stacks.

1. Login with the account already created and authenticate using the Pulumi CLI.
    ```sh
    $ pulumi login
    ```
    Pulumi will prompt you for an access token, including a method to launch your web browser to easily obtain one access token. Also, you can use the `PULUMI_ACCESS_TOKEN` environment variable to set the Pulumi token.

2. Create the Pulumi project and stack.
    Create a file  from `Pulumi.yml.example`  and set it the name to Pulumi.yml.
    To create the project and stack, run:
    ```sh
    $ pulumi stack init <STACK_NAME>
    ```
3. Create a Python virtual environment.
    Install the necessary packages.

    ```bash
    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip3 install -r requirements.txt
    ```
4. Set the AWS Configuration.
    Pulumi creates a file named Pulumi.<Stack_Name>.yml with some configurations by default, for instance, the AWS Region. These configurations can be accessed through the Python code.
    For this project you need to set two configurations for each stack, the AWS region in which you want to create the resources and the AWS profile that contains the AWS credentials.

    Configure the AWS credentials in your laptop(for Linux  ~/.aws/credentials), you need to use the following format:

    ```bash
    [Profile_name]
    aws_access_key_id = Replace_for_correct_Access_Key
    aws_secret_access_key = Replace_for_correct_Secret_Key
    ```

    Run the following commands to set the configurations in the stack

    ```bash
    $ pulumi config set  aws_region <AWS_Region>

    $ pulumi config set  aws_profile <AWS_profile>
    ```
# Deploy

You can review the resources that Pulumi will create or modify.
```bash
$ pulumi preview --json
```

If you are sure about the changes, you can proceed and apply them.
```bash
$ pulumi up
```

# Destroy
If you do not want to keep the resources created and you want to delete the stack, run:

```bash
$ pulumi destroy

$ pulumi stack rm

$ pulumi logout
```

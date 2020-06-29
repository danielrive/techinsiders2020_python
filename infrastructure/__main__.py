import os
import pulumi
from dotenv import load_dotenv
import pulumi_aws as aws
from aws_components.networking import aws_vpc

# load env variables
load_dotenv()

# creating custom aws provider
aws_config = aws.Provider("aws",
                          region=os.getenv("region"),
                          profile=os.getenv("profile"))

if __name__ == "__main__":
    vpc_microservice = aws_vpc.vpc("10.11.0.0/16", "test", 2, aws_config)

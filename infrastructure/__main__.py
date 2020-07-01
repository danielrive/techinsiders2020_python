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
    cidr_public=["10.11.1.0/24","10.11.2.0/24"] # CIDR block for publics subnets
    cidr_private=["10.11.100.0/24","10.11.101.0/24"]  # CIDR block for privates subnets
    
    vpc_microservice = aws_vpc.vpc("danielr","10.11.0.0/16",cidr_public,cidr_private ,aws_config)
    net_info = vpc_microservice.create_basic_networking()




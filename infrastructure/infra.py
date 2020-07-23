import os
import pulumi
from dotenv import load_dotenv
import pulumi_aws as aws
from aws_components.networking import aws_vpc
from aws_components.ALB import aws_alb
from aws_components.security import aws_sg
from aws_components.security_identity import aws_iam
from aws_components.containers import aws_ecs
from aws_components.dynamodb import aws_dynamodb

# from pulumi_docker import Image, ImageRegistry, DockerBuild

# Pulumi configs
config = pulumi.Config()

# ARNs
policy_ecs = 'arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy'

# load env variables
load_dotenv()

# Provider for testing
aws_config_testing = aws.Provider(
     'aws_testing',region='us-west-2',
     profile='testing_profile'
)

##### creating custom aws provider

aws_config = aws.Provider(
     'aws',region=config.require('aws_region'),
     profile=config.require('aws_profile')
)

Azs_Availables = aws.get_availability_zones(
            state="available", opts=pulumi.ResourceOptions(provider=aws_config)
)



# Networking creation
cidr_public = ['10.11.1.0/24', '10.11.2.0/24']
cidr_private = ['10.11.100.0/24', '10.11.101.0/24']

vpc_microservice = aws_vpc.vpc(
    'techinsiders', '10.11.0.0/16', cidr_public, cidr_private, Azs_Availables, aws_config
)
net_info = vpc_microservice.create_basic_networking()

# Security group
rule_alb_ingress = [
    {
       'description': 'allow_https',
       'fromPort': 443,
       'toPort': 443,
       'protocol': 'tcp',
       'cidrBlocks': ['0.0.0.0/0'],
    },
    {
       'description': 'allow_http',
       'fromPort': 80,
       'toPort': 80,
       'protocol': 'tcp',
       'cidrBlocks': ['0.0.0.0/0'],
    },
]

rule_alb_egress = [
    {
       'description': 'all_traffic',
       'fromPort': 0,
       'toPort': 0,
       'protocol': '-1',
       'cidrBlocks': ['0.0.0.0/0'],
    }
]

# SG ALB creation
security_group = aws_sg.aws_sg(aws_config)

alb_sg = security_group.create_sg(
    'alb', net_info['vpc_info'].id, rule_alb_ingress, rule_alb_egress
)

# SG Task
rule_tasks_ingress = [{
                        'description': 'allow_port_app',
                        'fromPort': 5000,
                        'toPort': 5000,
                        'protocol': 'tcp',
                        'cidrBlocks': ['0.0.0.0/0'],
                     }]

rule_tasks_egress = [{
                        'description': 'all_traffic',
                        'fromPort': 0,
                        'toPort': 0,
                        'protocol': '-1',
                        'cidrBlocks': ['0.0.0.0/0'],
                    }]
    
task_sg = security_group.create_sg(
    'ecs-task', net_info['vpc_info'].id, rule_tasks_ingress, rule_tasks_egress
)

# ALB creation
alb = aws_alb.aws_alb(
    'techinsiders', net_info['public_subnets'], False, [alb_sg.id], aws_config
)

create_alb = alb.create_alb()

tg_micro_health = {
       'enabled': True,
       'healthyThreshold': 3,
       'interval': 6,
       'matcher': 200,
       'path': '/',
       'port': 5000,
       'protocol': 'HTTP',
       'timeout': 5,
       'unhealthyThreshold': 2,
}

tg_ecs = alb.create_tg(80, 'HTTP', 'ip', tg_micro_health)

# Create Listener, specify the variable default_action following this format
# default_action= ['forward',arn_tg] ---> for forward to tg
# default_action= ['redirect',port,protocol] ---> for http to https redirect

listener_micro = alb.create_listener('HTTP', 80, ['forward', tg_ecs['tg_arn']])

# dynamoDB table
dynamo_tables = aws_dynamodb.aws_dynamodb(
    'dynamodb-micro', 'PAY_PER_REQUEST', aws_config
)

attributes_booktable = [{'name': 'id', 'type': 'S',}]
dynamo_tables.create_table('books', attributes_booktable, 'id')

# # Containers

# # ECS Creation

# # IAM Roles
ecs_iam = aws_iam.iam('ecs_iam', aws_config)
execution_role = ecs_iam.create_role('exec_role_micro', 'ecs')
task_role = ecs_iam.create_role('task_role_micro', 'ecs')

dynamo_policy_json = open('./IAM_policies/dynamodb_policy.json', 'r')
dynamo_iam_policy = ecs_iam.create_policy('policy-dynamodb', dynamo_policy_json.read())
    
# #attach policies

ecs_iam.attach_policy('policy-attach-exec-role', policy_ecs, execution_role.id )
ecs_iam.attach_policy('policy-attach-task-role', policy_ecs, task_role.id )
ecs_iam.attach_policy('dynamo-policy-attach', dynamo_iam_policy.arn, task_role.id )

# # ECS components

ecs_aws = aws_ecs.aws_ecs('techinsiders', aws_config)

#  ECR registry
ecs_aws.create_ecr_repo('tech-insiders-books', False, 'MUTABLE')

task_micro = ecs_aws.create_taskdf(
     'task-definition-books', '512', '1024', task_role.arn, execution_role.arn
)

services_tg_mapping = [ [tg_ecs['tg_arn'], 'micro-python', '5000'] ]
    
ecs_service = ecs_aws.create_service(
    'resource-python',
    1,
    1,
    services_tg_mapping,
    net_info['private_subnets'],
    task_sg.id
)

    


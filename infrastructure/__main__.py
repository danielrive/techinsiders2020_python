import os
import pulumi
from dotenv import load_dotenv
import pulumi_aws as aws
from aws_components.networking import aws_vpc
from aws_components.ALB import aws_alb
from aws_components.security import aws_sg
from aws_components.security_identity import aws_iam
from aws_components.containers import aws_ecs

# Pulumi configs
config = pulumi.Config()

# load env variables
load_dotenv()

# creating custom aws provider
aws_config = aws.Provider('aws',
                          region=config.require('aws_region'),
                          profile=config.require('aws_profile'))

if __name__ == '__main__':
    
    # Networking creation
    cidr_public=['10.11.1.0/24','10.11.2.0/24']  # CIDR Block for publics subnets
    cidr_private=['10.11.100.0/24','10.11.101.0/24'] # CIDR Block for publics subnets

    # VPC creation
    vpc_microservice = aws_vpc.vpc('danielr','10.11.0.0/16',cidr_public,cidr_private ,aws_config)
    
    net_info = vpc_microservice.create_basic_networking()

    # Security group
    rule_alb_ingress = [{
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
                       }]

    rule_alb_egress = [{
                        'description': 'all_traffic',
                        'fromPort': 0,
                        'toPort': 0,
                        'protocol': '-1',
                        'cidrBlocks': ['0.0.0.0/0'],
                       }]
    # SG ALB creation 
    security_group = aws_sg.aws_sg('alb-sg', net_info['vpc_id'], rule_alb_ingress, rule_alb_egress, aws_config)

    alb_sg = security_group.create_sg()
    
    # ALB creation 
    alb = aws_alb.aws_alb('danielr', net_info['public_subnets'], False, [alb_sg['sg_id']], aws_config)
    

    create_alb = alb.create_alb()
    
    tg_micro_health = { 
                        'enabled' : True,
                        'healthyThreshold': 3,
                        'interval': 6,
                        'matcher': 200,
                        'path': '/',
                        'port': 80,
                        'protocol': 'HTTP',
                        'timeout': 5,
                        'unhealthyThreshold': 2
                    }

    tg_ecs = alb.create_tg(80, 'HTTP', 'ip', tg_micro_health)
    
    # Create Listener, specify the variable default_action following this format
        # default_action= ['forward',arn_tg] ---> for forward to tg
        # default_action= ['redirect',port,protocol] ---> for http to https redirect

    listener_micro = alb.create_listener('HTTP',80, ['forward',tg_ecs['tg_arn']])

    # ECS Creation
      # IAM Roles
    ecs_iam = aws_iam.iam('ecs_iam', aws_config)
    execution_role = ecs_iam.create_role('exec_role_micro', 'ecs')
    task_role = ecs_iam.create_role('task_role_micro', 'ecs')
      
      # ECS components
    ecs_aws = aws_ecs.aws_ecs('danielr-ecs', aws_config)
    
    task_micro = ecs_aws.create_taskdf('512', '1024', task_role['role_arn'], execution_role['role_arn'])

    services_tg_mapping = [ [tg_ecs['tg_arn'], 'micro-service-tech-globant', '80'] ]
    
    ecs_service = ecs_aws.create_service('python_micro', 1, 1, services_tg_mapping, net_info['private_subnets'], alb_sg['sg_id'])


    



import os
import pulumi
from dotenv import load_dotenv
import pulumi_aws as aws
from aws_components.networking import aws_vpc
from aws_components.ALB import aws_alb
from aws_components.security import aws_sg

# load env variables
load_dotenv()

# creating custom aws provider
aws_config = aws.Provider('aws',
                          region=os.getenv('region'),
                          profile=os.getenv('profile'))

if __name__ == '__main__':
    # Networking creation
    cidr_public=['10.11.1.0/24','10.11.2.0/24']
    cidr_private=['10.11.100.0/24','10.11.101.0/24']

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
    security_group = aws_sg.aws_sg(aws_config)

    alb_sg = security_group.create_sg('sg_alb',net_info['vpc_id'],rule_alb_ingress,rule_alb_egress)
    
    # ALB creation 
    alb = aws_alb.aws_alb(aws_config)
    

    create_alb = alb.create_alb('danielr',net_info['private_subnets'],True,[alb_sg['sg_id']])
    
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

    tg_ecs = alb.create_tg(80,'HTTP','ip',tg_micro_health)
    
    # Create Listener, specify the variable default_action following this format
        # default_action= ['forward',arn_tg] ---> for forward to tg
        # default_action= ['redirect',port,protocol] ---> for forward to tg

    listenre = alb.create_listener("HTTP",80, ['forward',tg_ecs['tg_arn']])



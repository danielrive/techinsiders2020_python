import os
import pulumi
import pulumi_aws as aws
import string
import random

class aws_alb():
    def __init__(self,provider):
        self.provider = provider
        self.alb = []

    def create_alb(self,name, subnets, internal,security_groups):
        self.name = name
        alb = aws.lb.LoadBalancer(name,
                    enable_deletion_protection=False,
                    internal = internal,
                    load_balancer_type = 'application',
                    security_groups = security_groups,
                    subnets = subnets,
                    __opts__ = pulumi.ResourceOptions(provider=self.provider),
                    tags={
                          'Name': name,
                          'Createdby': 'Pulumi'
                    })
        alb_info = { 
                    'alb_arn':  alb.arn,
                    'alb_dns': alb.dns_name,
                    'alb_zone_id': alb.zone_id
                    }

        return alb_info

    def create_listener(self, protocol, port, default_action, certificate = "none" ):
        pass

    def create_rule(self, rule):
        pass

    def create_tg(self):
        pass
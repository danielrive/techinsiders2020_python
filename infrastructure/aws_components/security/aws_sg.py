import os
import pulumi
import pulumi_aws as aws


class aws_sg():
    def __init__(self, provider):
        self.provider = provider

    def create_sg(self,name, vpc_id, rule_ingress,rule_egress):

        sg = aws.ec2.SecurityGroup(name, 
                    description = 'Allow TLS inbound traffic',
                    vpc_id = vpc_id,
                    ingress = rule_ingress,
                    egress = rule_egress,
                    __opts__= pulumi.ResourceOptions(provider=self.provider),
                    tags={
                          'Name': name,
                          'Createdby': 'Pulumi'
                    })

        sg_info = { 'sg_arn' :sg.arn,
                    'sg_id' : sg.id
                  }
        
        return sg_info
    
    def add_ingress_rule(self,rule):
        pass
    def add_egress_rule(self,rule):
        pass
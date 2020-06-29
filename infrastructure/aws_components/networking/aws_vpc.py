import os
import pulumi
import pulumi_aws as aws
import ipaddress as ip
'''
vpc module
'''


class vpc():
    def __init__(self, net_address, subnet_mask, name, provider):
        self.net_address = net_address
        self.subnet_mask = subnet_mask
        self.name = name
        self.provider = provider
        cidr_subnets = []

    def calculate_cidr(self):
        addresses = ip_network(self.net_address)
        cidr_subnets = addresses[0:3]

    def create_vpc(self):
        if ipv4:
            aws.ec2.Vpc("vpc_pulumi_{}".format(self.name),
                        cidr_block=self.cidr,
                        enable_dns_support=True,
                        enable_dns_hostnames=True,
                        __opts__=pulumi.ResourceOptions(provider=self.provider)
                        tags={
                            Createdby="Pulumi"
            })

    def create_subnet(self, public):
        pass

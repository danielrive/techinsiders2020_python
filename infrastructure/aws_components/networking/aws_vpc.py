import pulumi
import pulumi_aws as aws
import ipaddress as ip


class vpc():
    '''
    A class used to represent an AWS Networking resources

    Methods
    -------
    create_basic_networking()
        Creates a
    '''
    def __init__(self,name, net_address, cidr_public, cidr_private, provider):
        '''
        Parameters
        ------------
        name : str
            An unique name to assign to VPC and resouces related
        net_address : str
            An IP address to assing to the VPC, specify the Mask by /
            This is the address for the network
        cidr_public : list
            A CIDR block to assing to public subnets, should be into the net_address specified
        cidr_private : list
            A CIDR block to assing to private subnets, should be into the net_address specified
        provider: str
            A pulumi provider configurations, according to this attribute the AWS resources
            will be created in the region and credentials specified.
        '''
        self.name = name
        self.net_address = net_address
        self.cidr_public = cidr_public
        self.cidr_private = cidr_private
        self.provider = provider
        self.public_subnets = []
        self.private_subnets = []
        self.az_available = aws.get_availability_zones(state='available',opts=pulumi.ResourceOptions(provider=self.provider))

    def create_basic_networking(self):
        ''' 
        Creates the components to support a basic networking following the best AWS
        practices like two AZ for HA, public and private subnets.
        This method will create:
            2 public subnets with a route table(for both) and internet gateway
            2 privates subnets with a route table(for both) and NAT Gateway
        Parameters
        -----------
        none

        Returns 
        --------
        networking : dict
            A dict with the vpc_id, a list with subnet_id(public and private)

        '''
        vpc_pulumi = aws.ec2.Vpc('vpc_pulumi_{}'.format(self.name),
                                 cidr_block=self.net_address,
                                 enable_dns_support=True,
                                 enable_dns_hostnames=True,
                                 __opts__=pulumi.ResourceOptions(
                                     provider=self.provider),
                                 tags={
                                     'Name': 'vpc_{}'.format(self.name),
                                     'Createdby': 'Pulumi'
                                })

        # Public subnets creation
        for i in range(len(self.cidr_public)):
            self.public_subnets.append(
                    aws.ec2.Subnet('subnet_public_{}_{}'.format(self.name, i),
                        cidr_block=str(self.cidr_public[i]),
                        availability_zone=self.az_available.names[i],
                        __opts__=pulumi.ResourceOptions(provider=self.provider),
                        tags={
                             'Name': 'subnet_public_{}_{}'.format(self.name, i),
                             'Createdby': 'Pulumi'
                        },
                        vpc_id=vpc_pulumi.id
            ))

        # Private subnets creation
        for i in range(len(self.cidr_private)):
            self.private_subnets.append(
                    aws.ec2.Subnet('subnet_private_{}_{}'.format(self.name, i),
                        cidr_block=str(self.cidr_private[i]),
                        availability_zone=self.az_available.names[i],
                        __opts__=pulumi.ResourceOptions(provider=self.provider),
                        tags={
                             'Name': 'subnet_private_{}_{}'.format(self.name, i),
                             'Createdby': 'Pulumi'
                        },
                        vpc_id=vpc_pulumi.id
            ))

        # Nat Gateway creation
        eip = aws.ec2.Eip('eip_{}'.format(self.name),
                 vpc=True,
                 __opts__=pulumi.ResourceOptions(provider=self.provider),
                 tags={
                     'Name': 'eip_{}'.format(self.name),
                     'Createdby': 'Pulumi'
                 })

        natgw = aws.ec2.NatGateway('natgw_{}'.format(self.name),
                    allocation_id=eip.id,
                    subnet_id=self.public_subnets[0].id,
                    __opts__=pulumi.ResourceOptions(provider=self.provider),
                    tags={
                         'Name': 'natgw_{}'.format(self.name),
                         'Createdby': 'Pulumi'
                    })

        # Internet Gateway creation
        igw = aws.ec2.InternetGateway('igw_{}'.format(self.name),
                    vpc_id = vpc_pulumi.id,
                    __opts__= pulumi.ResourceOptions(provider=self.provider),
                    tags={
                          'Name': 'igw_{}'.format(self.name),
                          'Createdby': 'Pulumi'
                        })
                        
        # Route Tables Creation
        # Public RT
        rt_public = aws.ec2.RouteTable('rt_public_{}'.format(self.name),
                        routes=[
                           {
                                'cidr_block': '0.0.0.0/0',
                                'gateway_id': igw.id,
                           }
                        ],
                        __opts__= pulumi.ResourceOptions(provider=self.provider),
                        vpc_id = vpc_pulumi.id,
                        tags={
                                'Name': 'rt_public_{}'.format(self.name),
                                'Createdby': 'Pulumi'
                        })
        
        # Private RT
        rt_private = aws.ec2.RouteTable('rt_private_{}'.format(self.name),
                        routes=[
                           {
                                'cidr_block': '0.0.0.0/0',
                                'gateway_id': natgw.id,
                           }
                        ],
                        __opts__= pulumi.ResourceOptions(provider=self.provider),
                        vpc_id = vpc_pulumi.id,
                        tags={
                                'Name': 'rt_private_{}'.format(self.name),
                                'Createdby': 'Pulumi'
                        })        
    
        # Route association
        # public rt
        for i in range(len(self.public_subnets)):
            rt_association_pub = aws.ec2.RouteTableAssociation('rt_association_pub_{}'.format(i),
                                 subnet_id=self.public_subnets[i].id,
                                 route_table_id=rt_public.id,
                                 __opts__= pulumi.ResourceOptions(provider=self.provider))
        # private rt
        for i in range(len(self.private_subnets)):
            rt_association_priv = aws.ec2.RouteTableAssociation('rt_association_priv_{}'.format(i),
                                 subnet_id=self.private_subnets[i].id,
                                 route_table_id=rt_private.id,
                                 __opts__= pulumi.ResourceOptions(provider=self.provider))
        
        # Response
        
        networking = {  
                        'vpc_id':vpc_pulumi.id,
                        'public_subnets': [__item.id for __item in self.public_subnets],
                        'private_subnets': [__item.id for __item in self.private_subnets]
     #                   'public_subnets': self.private_subnets
                    }

        return networking

    def create_subnet(self, name, type):
         ''' 
        Creates a subnet according to the type specified(private or public)
        
        Parameters
        -----------
        name : str
            the unique name for the subnet
        
        type : str
            valid values, public or private

        Returns 
        --------
        subnet : dict
            A dict with the subnet_id created

        '''
        pass


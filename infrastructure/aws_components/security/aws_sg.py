import pulumi
import pulumi_aws as aws


class aws_sg():
    '''
    A class used to represent a AWS Security Group

    Methods
    -------
    create_sg()
        Creates a Security Group with the first rules(ingress and egress)
    create_rule(name,type,ip,port,description)
        Creates a Security Group rule and associates it to SG created
    '''
    def __init__(self, name, vpc_id, rule_ingress, rule_egress, provider):
        '''
        Parameters
        ------------
        name : str
            An unique name to assign to the Security Group
        vpc_id : str
            A VPC ID to associate the Security Group
        rule_ingress : list
            A list of dicts with the ingress rule to create, the format fot the dict should 
            be like
                        {'description': 'allow_https',
                        'fromPort': 443,
                        'toPort': 443,
                        'protocol': 'tcp',
                        'cidrBlocks': ['0.0.0.0/0']}

        rule_egress : list
            A list of dicts with the egress rule to create

        provider: str
            A pulumi provider configurations, according to this attribute the AWS resources
            will be created in the region and credentials specified.
        '''
        self.name = name
        self.vpc_id = vpc_id
        self.rule_ingress = rule_ingress
        self.rule_egress = rule_egress
        self.provider = provider


    def create_sg(self):
        '''
        Creates a security group into the vpc specified, assigns the rules passed in the lists
        
        Parameters
        -----------
        none

        Returns 
        --------
        sg_info : dict
            A dict with the sg_id and ARN

        '''
        sg = aws.ec2.SecurityGroup('sg-' + self.name, 
                    description = 'sg-' + self.name,
                    vpc_id = self.vpc_id,
                    ingress = self.rule_ingress,
                    egress = self.rule_egress,
                    __opts__= pulumi.ResourceOptions(provider=self.provider),
                    tags={
                          'Name': self.name,
                          'Createdby': 'Pulumi'
                    })

        # returns
        sg_info = { 'sg_arn' :sg.arn,
                    'sg_id' : sg.id
                  }
        
        return sg_info
    
    def add_rule(self,name, type, ip, port, description="none"):
        '''
        Creates a ingress or egress rules and assign to the SG created
        
        Parameters
        -----------
        name : str
            A name to assign to the rule
        type : str
            Type of rule, ingress or egress
        ip : str
            A CIDR block to allow in the rule
        port : int
            the port to open
        description : str
            optional
            A little description for the rule to create
        
        Returns 
        --------
        none
        '''
        pass
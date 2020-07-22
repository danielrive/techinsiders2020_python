import pulumi
import pulumi_aws as aws


class aws_sg:
    '''
    A class used to represent a AWS Security Group
    Methods
    -------
    create_sg()
        Creates a Security Group with the first rules(ingress and egress)
    create_rule(name,type,ip,port,description)
        Creates a Security Group rule and associates it to SG created
    '''
    def __init__(self, provider):
        '''
        Parameters
        ------------
        name : str
            An unique name to assign to the Security Group
        vpc_id : str
            A VPC ID to associate the Security Group
        provider: str
            A pulumi provider configurations, according to this attribute the AWS resources
            will be created in the region and credentials specified.
        '''
        self.provider = provider

    def create_sg(self, name, vpc_id, rule_ingress, rule_egress):
        '''
        Creates a security group into the vpc specified, assigns the rules passed in the lists
        
        Parameters
        -----------
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
        Returns 
        --------
        sg : Pulumi output
            a object with informationabout the resource created
        '''
        sg = aws.ec2.SecurityGroup(
            name,
            description="Allow TLS inbound traffic",
            vpc_id=vpc_id,
            ingress=rule_ingress,
            egress=rule_egress,
            __opts__=pulumi.ResourceOptions(provider=self.provider),
            tags={"Name": name, "Createdby": "Pulumi"},
        )

        return sg

    def add_ingress_rule(self, rule):
        pass

    def add_egress_rule(self, rule):
        pass

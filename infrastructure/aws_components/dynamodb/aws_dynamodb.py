import pulumi
import pulumi_aws as aws


class aws_dynamodb():
    '''
    A class used to represent a dynamodb with his components

    Methods
    -------
    create_table()
        Creates an AWS ALB with the security group and subtnes specified
    
    '''

    def __init__(self, name, billing_mode,  provider):
        '''
        Parameters
        ------------
        name : str
            An unique name to assign to DynamoDB resources
        billing_mode : str
            

        '''
        self.name = name
        self.billing_mode = billing_mode
        self.provider = provider

    def create_table(self, table_name, attributes, hash_key):
        '''
        creates a dynamoDB table with the parameters specified
        
        Parameters
        ------------
        table_name : string
            An unique name to assign to DynamoDB resources
        attributes : dict
            A dict with the attributes to create into dynamodb table
        hash_key : string
            A hash key for the dynamoDB table

        Returns
        --------
        none
        '''
        basic_dynamodb_table = aws.dynamodb.Table(table_name,
                name = table_name,
                attributes = attributes,
                billing_mode = self.billing_mode,
                hash_key = hash_key,
                tags={
                    'Createdby': 'Pulumi',
                    'Name': table_name,
                },
                __opts__= pulumi.ResourceOptions(provider=self.provider))
import pulumi
import pulumi_aws as aws

class iam():
    '''
    A class used to represent AWS IAM resources

    Methods
    -------
    create_role(aws_service)
        Creates an IAM role associate to AWS service
    '''
    def __init__(self, name, provider):
        '''
        Parameters
        ------------
        name : str
            An unique name to assign to the IAM resources

        provider: str
            A pulumi provider configurations, according to this attribute the AWS resources
            will be created in the region and credentials specified.
        '''
    
        self.name = name
        self.provider = provider

        self.aws_services = {
                            'ecs' : 'ecs-tasks.amazonaws.com'
                            'ec2' : 'ec2.amazonaws.com'
                       }
        
    def create_role(self, aws_service ):
        '''
        Parameters
        ------------
        aws_service : str
            An AWS service name that will be associated to the IAM Role, the name specify will be mapped
            in the aws_services dict
        
        Return
        -------
        role_info : dict
            A dict with the IAM ARN role
        '''
        
        role_policy_doc = aws.iam.get_policy_document(statements=[{
                'actions': ['sts:AssumeRole'],
                'principals': [{
                    'identifiers': [aws_services[aws_service]],
                    'type': 'Service',
                }],
            }],
            opts = pulumi.ResourceOptions(provider=self.provider))

        ecs_role = aws.iam.Role('ecs_role'+name,
                    assume_role_policy = role_policy_doc.json,
                    __opts__= pulumi.ResourceOptions(provider=self.provider))
        
        role_info = {
                        'role_arn': ecs_role.arn
                    }

        return role_info
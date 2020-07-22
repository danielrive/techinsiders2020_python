import pulumi
import pulumi_aws as aws

class iam():
    '''
    A class used to represent AWS IAM resources

    Methods
    -------
    create_role(name_role, aws_service)
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
                            'ecs' : 'ecs-tasks.amazonaws.com',
                            'ec2' : 'ec2.amazonaws.com'
                       }
        
    def create_role(self, name_role, aws_service ):
        '''
        Parameters
        ------------
        name_role : str
            An unique name to assign to the IAM resources

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
                    'identifiers': [self.aws_services[aws_service]],
                    'type': 'Service',
                }],
            }],
            opts = pulumi.ResourceOptions(provider=self.provider))

        ecs_role = aws.iam.Role(name_role+self.name,
                    assume_role_policy = role_policy_doc.json,
                    __opts__= pulumi.ResourceOptions(provider=self.provider))
        
        role_info = {
                        'role_arn': ecs_role.arn,
                        'role_name': ecs_role.id
                    }

        return role_info

    def attach_policy(self, name, arn_policy, arn_user):
        '''
        Parameters
        ------------
        name : str
            An identification for the attachment
        arn_policy : str
            ARN Policy to attach 

        arn_user : list
            The ARN of Roles, users or groups that will have the policy
        
        Return
        -------
        none
        '''

        aws.iam.RolePolicyAttachment(name,
                        policy_arn = arn_policy,
                        role = arn_user,
                        __opts__= pulumi.ResourceOptions(provider=self.provider))


    def create_policy(self, name, json_policy):
        '''
        Parameters
        ------------
        name : str
            The policy name to create
        json_policy : str
            A json with the IAM policy to create

        Return
        -------
        policy_info : dict
            ARN policy created
        '''
        policy = aws.iam.Policy('policy' + name,
                        name = 'policy' + name,
                        path='/',
                        policy = json_policy,
                        __opts__= pulumi.ResourceOptions(provider=self.provider))

        policy_info = {
                        'policy_arn' : policy.arn
                      }
        
        return policy_info
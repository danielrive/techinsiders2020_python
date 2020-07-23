import unittest
import pulumi


class MyMocks(pulumi.runtime.Mocks):
    def new_resource(self, type_, name, inputs, provider, id_):
        if type_ == 'pulumi:providers:aws':
            state = {
                'id': '12345',
            }
            return ['12345', dict(inputs, **state)]
        if type_ == 'aws:lb/listener:Listener':
            state = {
                'arn': 'arn:aws:elasticloadbalancing:us-west-2:123456789012:listener/app/my-load-balancer/50dc6c495c0c9188/f2f7dc8efc522ab2',
            }
            return ['listener-12345678', dict(inputs, **state)]
        else:
            return [name + '_id', inputs]
    def call(self, token, args, provider):
        if token == 'aws:index/getAvailabilityZones:getAvailabilityZones':
            return {'names':['us-west-2a','us-west-2b']}
        elif token == 'aws:iam/getPolicyDocument:getPolicyDocument':
            return {
                'actions': ['sts:AssumeRole'],
                'principals': [{
                    'identifiers': ['ecs'],
                    'type': 'Service',
                }],
            }
        else:
            return {}

pulumi.runtime.set_mocks(MyMocks())

# Now actually import the code that creates resources, and then test it.
from aws_components.ALB import aws_alb
from aws_components.security import aws_sg
import pulumi_aws as aws 

class TestingWithMocks(unittest.TestCase):
    aws_config_testing = aws.Provider(
               'aws_testing',region='us-west-2',
               profile='testing_profile'
    )
    # Test if the service has tags and a name tag.
    @pulumi.runtime.test
    def test_sec_groups_tags(self):
        aws_config_testing = aws.Provider(
                'aws_testing',region='us-west-2',
                profile='testing_profile'
        )
        security_group_testing = aws_sg.aws_sg(aws_config_testing)

        rule_alb_ingress_testing = [{'description': 'allow_https','fromPort': 443,
                            'toPort': 443,'protocol': 'tcp','cidrBlocks': ['0.0.0.0/0'],
                            }]

        rule_alb_egress_testing = [{'description': 'all_traffic','fromPort': 0,'toPort': 0,
                            'protocol': '-1','cidrBlocks': ['0.0.0.0/0'],
                        }]

        sg_tesging = security_group_testing.create_sg(
            'alb', 'vpc-123456', rule_alb_ingress_testing, rule_alb_egress_testing
        )
        def check_tags(args):
            urn,tags = args
            self.assertIsNotNone(tags, f'server {urn} must have tags')
            self.assertIn('Name', tags, f'server {urn} must have a name tag')
            self.assertIn('Createdby', tags, f'server {urn} must have a name tag')

        return pulumi.Output.all(sg_tesging.urn,sg_tesging.tags).apply(check_tags)
    

    # Testing alb listener method
    @pulumi.runtime.test
    def test_listener_method(self):
        aws_config_testing = aws.Provider(
                'aws_testing',region='us-west-2',
                profile='testing_profile'
        )        
        alb_testing= aws_alb.aws_alb(
               'alb_testing', ['subnet-123456','subnet-78011'], False, ['sg-123456'], aws_config_testing
        )
        create_alb_testing = alb_testing.create_alb()
        listener_test2 = alb_testing.create_listener('HTTPs', 80, ['redirect', 443, 'HTTPS'])
        def check_arn(args):
            urn,arn = args
            print(arn)
            self.assertIsNotNone(arn, f'the listener {urn} must exist')
            self.assertIsNotNone(arn, f'the listener {urn} must exist')
        return pulumi.Output.all(listener_test2.urn,listener_test2.arn).apply(check_arn)
    


        
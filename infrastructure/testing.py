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
import infra
from aws_components.ALB import aws_alb
class TestingWithMocks(unittest.TestCase):
    # Test if the service has tags and a name tag.
    @pulumi.runtime.test
    def test_sec_groups_tags(self):
        def check_tags(args):
            urn,tags = args
            self.assertIsNotNone(tags, f'server {urn} must have tags')
            self.assertIn('Name', tags, f'server {urn} must have a name tag')
            self.assertIn('Createdby', tags, f'server {urn} must have a name tag')

        return pulumi.Output.all(infra.alb_sg.urn,infra.alb_sg.tags).apply(check_tags)
    
    # Testing alb listener method
    @pulumi.runtime.test
    def test_listener_method(self):
        alb_testing= aws_alb.aws_alb(
               'alb_testing', infra.net_info['public_subnets'], False, [infra.alb_sg.id], infra.aws_config
        )
        create_alb_testing = alb_testing.create_alb()
        listener_test = alb_testing.create_listener('HTTP', 80, ['forward', infra.tg_ecs['tg_arn']])
        listener_test2 = alb_testing.create_listener('HTTP', 80, ['redirect', 443, 'HTTPS'])
        def check_arn(args):
            urn,arn = args
            print(arn)
            self.assertIsNotNone(arn, f'the listener {urn} must exist')
            self.assertIsNotNone(arn, f'the listener {urn} must exist')
        return pulumi.Output.all(listener_test2.urn,listener_test2.arn).apply(check_arn)
    


        
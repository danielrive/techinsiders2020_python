import unittest
import pulumi
import pulumi_aws as aws
from aws_components.security_identity import aws_iam
from aws_components.networking import aws_vpc

class MyMocks(pulumi.runtime.Mocks):
    def new_resource(self, type_, name, inputs, provider, id_):
        return [name + '_id', inputs]
    def call(self, token, args, provider):
        return {}

pulumi.runtime.set_mocks(MyMocks())

# Now actually import the code that creates resources, and then test it.

from aws_components.security import aws_sg

class TestingWithMocks(unittest.TestCase):
    # @pulumi.runtime.test
    # def test_validate(self):
    #     aws_config = aws.Provider('aws',
    #                       region='us-west-2',
    #                       profile='danielglobant')
      
    #     def check_tags(args):
    #         urn,tags = args
    #         self.assertIsNotNone(tags, f'server {urn} must have tags')
    #         self.assertIn('Name', tags, f'server {urn} must have a name tag')
    #         self.assertIn('Createdby', tags, f'server {urn} must have a name tag')

    #     return pulumi.Output.all(sg_test.urn,sg_test.tags).apply(check_tags)

    # Test if the service has tags and a name tag.
    aws_config = aws.Provider('aws',
                          region='us-west-2',
                          profile='danielglobant')
        # SG ALB creation example
    security_group = aws_sg.aws_sg(aws_config)

    sg_test = security_group.create_sg(
            'testing', 'vpc-test-id', ['test'], ['test']
        )
    @pulumi.runtime.test
    def test_sec_groups_tags(self):
        def check_tags(args):
            urn,tags = args
            self.assertIsNotNone(tags, f'server {urn} must have tags')
            self.assertIn('Name', tags, f'server {urn} must have a name tag')
            self.assertIn('Createdby', tags, f'server {urn} must have a name tag')

        return pulumi.Output.all(sg_test.urn,sg_test.tags).apply(check_tags)
    


        
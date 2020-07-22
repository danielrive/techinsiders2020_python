import pulumi
import pulumi_aws as aws


class iam:
    def __init__(self, provider):
        self.provider = provider
        self.aws_services = {"ecs": "ecs-tasks.amazonaws.com"}

    def create_role(self, name, aws_service):
        role_policy_doc = aws.iam.get_policy_document(
            statements=[
                {
                    "actions": ["sts:AssumeRole"],
                    "principals": [
                        {
                            "identifiers": [self.aws_services[aws_service]],
                            "type": "Service",
                        }
                    ],
                }
            ],
            opts=pulumi.ResourceOptions(provider=self.provider),
        )

        ecs_role = aws.iam.Role(
            "ecs_role" + name,
            assume_role_policy=role_policy_doc.json,
            __opts__=pulumi.ResourceOptions(provider=self.provider),
        )

        role_info = {"role_arn": ecs_role.arn}

        return role_info

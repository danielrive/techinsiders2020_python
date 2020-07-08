import pulumi
import pulumi_aws as aws
import json

class aws_ecs():
    def __init__(self, name, provider):
        self.name = name
        self.provider = provider
        self.task_def = []
        self.cluster_info = aws.ecs.Cluster('cluster_'+name,
                                __opts__ = pulumi.ResourceOptions(provider = provider),
                                tags={
                                    'Name': 'cluster_'+name,
                                    'Createdby': 'Pulumi'
                                })
    
    def create_taskdf(self, cpu, memory, role_task = None, execution_role = None ):
        container_definition = open('./aws_components/containers/containers_micro.json', 'r')

        self.task_def = aws.ecs.TaskDefinition('tf_'+self.name,
                                family = 'tf_'+self.name,
                                cpu = cpu,
                                memory = memory,
                                execution_role_arn = execution_role,
                                task_role_arn = role_task,
                                network_mode = 'awsvpc',
                                requires_compatibilities = ['FARGATE'],
                                container_definitions = container_definition.read(),
                                __opts__ = pulumi.ResourceOptions(provider = self.provider))

    def create_service(self,name_service,min_task,max_tasks,target_groups,subnets,sg):

        mapping_alb = []
        for i in range(len(target_groups)):
            mapping_alb.append( { 'target_group_arn': target_groups[i][0],
                    'container_name': target_groups[i][1],
                    'containerPort': target_groups[i][2],
                  })

        ecs_service = aws.ecs.Service('ecs_service_'+ name_service + self.name,
                    name = 'ecs_service_'+ name_service,
                    cluster = self.cluster_info.id,
                    task_definition = self.task_def.arn,
                    desired_count = min_task,
                    deployment_maximum_percent = 200,
                    deployment_minimum_healthy_percent = 100,
                    health_check_grace_period_seconds = 10,
                    launch_type = 'FARGATE',
                    load_balancers = mapping_alb,
                    network_configuration = {
                            'subnets': subnets,
                            'security_groups' : [sg]
                    },
                    __opts__ = pulumi.ResourceOptions(provider = self.provider))


    def create_auto_scaling():
        pass

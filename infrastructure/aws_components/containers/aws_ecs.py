import pulumi
import pulumi_aws as aws
import json

class aws_ecs():
    '''
    A class used to represent AWS ECS resources,creates an ECS cluster 

    Methods
    -------
    create_taskdf(cpu, memory, role_task, execution_role)
        Creates a task definition, this method receives some
        parameters and the container definitions are taken from the directory.
        The file containerdf_skeleton.json has a model with the parameters that are allowed.

    create_service(name_service, min_task, max_tasks, target_groups, subnets, sg)
        Creates a ECS service according to the task definition created.

    '''    
    def __init__(self, name, provider):
        '''
        Creates an ECS cluster with minimal configurations
        Parameters
        ------------
        name : str
            An unique name to assign to the ECS resources

        provider: str
            A pulumi provider configurations, according to this attribute the AWS resources
            will be created in the region and credentials specified.
        '''
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
        '''
        Creates a ECS task definition, the container definitions is taken
        from an external filestored in the directory created for this package, 
        there is a file named containerdf_skeleton.json that has a model to create
        a container definition, a container_definition variable has beed created
        that read a external file to create the TasK Definition

        Parameters
        ------------
        cpu : int
            CPU units to assign to the Task Definition, follow AWS documentation
            to select the correct values
        memory : int
            Memory units to assign to the Task Definition, follow AWS documentation
            to select the correct values
        role_task : str
            optional
            ARN role that the tasks will use.
        
        execution_role : str
            optional
            The ARN  for the execution to make pull of ECR image

        provider: str 
            A pulumi provider configurations, according to this attribute the AWS resources
            will be created in the region and credentials specified.
        
        Return
        -------
        none

        '''

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

    def create_service(self,name_service,min_task=1,max_tasks=1,target_groups,subnets,sg):
        '''
        Creates a ECS service, by default use fargate to launch the tasks

        Parameters
        ------------
        name_service : str
            A name to assing to the service to create
        min_task : int
            optional, default value 1
            min number of task to launch into the service
        max_tasks : int
            optional, default value 1
            max number of task to launch into the service
        
        target_groups : list
            A list with the ARNs of the target groups to associate the task

        subnets : list
            A list with the Subnets IDs to place the ECS tasks
        
        sg : str
            A Security Group ID to assign to the tasks
        
        provider: str 
            A pulumi provider configurations, according to this attribute the AWS resources
            will be created in the region and credentials specified.
        
        Return
        -------
        none
        
        '''
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

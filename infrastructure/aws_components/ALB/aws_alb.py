import pulumi
import pulumi_aws as aws


class aws_alb:
    '''
    A class used to represent a ALB with his components
    Methods
    -------
    create_alb()
        Creates an AWS ALB with the security group and subtnes specified
    
    create_listener(self,protocol, port, default_action, certificate='None')
        Creates and associates a listener to ALB already created
    create_rule(self, rule)
        Creates an ALB rule and associates with the listener specify
    create_tg(self ,port ,protocol, type, health_check)
        Creates an Target Group to be associate to listener
    '''
    def __init__(self, name, subnets, internal, security_groups, provider):
        '''
        Parameters
        ------------
        name : str
            An unique name to assign to ALB
        subnets : list
            An list with the subnets IDs in which the alb will be
        internal : bool
            The type of ALB to crete, for private ALB set this parameter to True
        securitygroups : list
            An list with the security groups IDs to attach to the ALB created 
        '''

        self.name = name
        self.subnets = subnets
        self.internal = internal
        self.security_groups = security_groups
        self.provider = provider
        self.alb = []

    def create_alb(self):
        '''
        creates ALB with the parameters specified
        
        Parameters
        ------------
        none
        Returns
        --------
        alb_info : dict
            A dict with the id, arn and zone_id of the ALB created
        '''
        self.alb = aws.lb.LoadBalancer(self.name,
                    enable_deletion_protection=False,
                    internal = self.internal,
                    load_balancer_type = 'application',
                    security_groups = self.security_groups,
                    subnets = self.subnets,
                    __opts__ = pulumi.ResourceOptions(provider = self.provider),
                    tags={
                          'Name': self.name,
                          'Createdby': 'Pulumi'
                    })
        alb_info = { 
                    'alb_arn':  self.alb.arn,
                    'alb_dns': self.alb.dns_name,
                    'alb_zone_id': self.alb.zone_id
                    }

        return alb_info

    def create_listener(self,protocol, port, default_action, certificate='None'):
        '''
        Creates/attaches a listener with the protocol and actions specified
        By default the certificate have been set to None, specify an arn to associate
        with the listener
        Parameters
        ------------
        protocol : str
            The protocol used for the listener to recieive the requests
        port : int
            A port in which the alb will listen the request
        default_action : list
            A list with the specifications to use as a default action,
            there are two option, redirect the request(301) or forward the request to Target Group
            the elements into the list depend of the action to take
                default_action= ['forward',arn_tg] ---> for forward to tg
                default_action= ['redirect',port,protocol] ---> for http to https redirect
        certificate : str
            An ARN of the AWS certicate that will use the listener, only apply gor https listeners
   
        Returns
        --------
        empty
        '''

        if default_action[0] == 'forward':
            action =  {
                        'target_group_arn': default_action[1],
                        'type': 'forward',
                     }
        elif default_action[0] == 'redirect':
            action = {
                        'redirect': {
                            'port': default_action[1],
                            'protocol': default_action[2],
                            'status_code': 'HTTP_301',
                        },
                        'type': 'redirect',
            }

        if protocol == 'HTTP':
            alb_listener = aws.lb.Listener('listener-{}-{}'.format(port,self.name),
                        default_actions = [action],
                        load_balancer_arn = self.alb.arn,
                        port = port,
                        protocol = protocol,
                        __opts__ = pulumi.ResourceOptions(provider = self.provider))
        else:
            alb_listener = aws.lb.Listener('listener-{}-{}'.format(port,self.name),
                        default_actions = [action],
                        certificate_arn = certificate,
                        ssl_policy = 'ELBSecurityPolicy-2016-08',
                        load_balancer_arn = self.alb.arn,
                        port = port,
                        protocol = protocol,
                        __opts__ = pulumi.ResourceOptions(provider = self.provider))


    def create_rule(self, rule):
        pass

    def create_tg(self ,port ,protocol, type, health_check):
        ''' 
        Creates a Target group to bu used for the ALB to send request
        
        Parameters
        ------------
        port : int
            The port in which the Target Group will listen the requests
           
        protocol : string
            The protocol used for the Target Group to recieive the requests   
        
        type : str
            Type of Target Group to create, ip or instance
        health_check : dict
            A dict with the configuration for the healh_checks, follow this structure
                        'enabled' : bool,
                        'healthyThreshold': int,
                        'interval': int,
                        'matcher': int,
                        'path': str,
                        'port': int,
                        'protocol': str,
                        'timeout': int,
                        'unhealthyThreshold': int
   
        Returns
        --------
        tg_info : dict
            A dict with the ID and ARN of the TG created
        
        '''        

        alb_tg = aws.lb.TargetGroup('tg-{}-{}'.format(port,self.name),
                                    port = port,
                                    name = 'tg-{}-{}'.format(port,self.name),
                                    protocol='HTTP',
                                    target_type = type ,
                                    deregistration_delay = 10,
                                    health_check = health_check,
                                    __opts__ = pulumi.ResourceOptions(provider = self.provider),
                                    vpc_id = self.alb.vpc_id
                                    )
        
        tg_info = {
                    'tg_arn': alb_tg.arn,
                    'tg_id': alb_tg.id,
                  }

        return tg_info
    
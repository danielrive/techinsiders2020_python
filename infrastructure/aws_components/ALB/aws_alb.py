import pulumi
import pulumi_aws as aws


class aws_alb():
    def __init__(self,provider):
        self.provider = provider
        self.alb = []

    def create_alb(self,name, subnets, internal,security_groups):
        self.name = name
        self.alb = aws.lb.LoadBalancer(name,
                    enable_deletion_protection=False,
                    internal = internal,
                    load_balancer_type = 'application',
                    security_groups = security_groups,
                    subnets = subnets,
                    __opts__ = pulumi.ResourceOptions(provider = self.provider),
                    tags={
                          'Name': name,
                          'Createdby': 'Pulumi'
                    })
        alb_info = { 
                    'alb_arn':  self.alb.arn,
                    'alb_dns': self.alb.dns_name,
                    'alb_zone_id': self.alb.zone_id
                    }

        return alb_info

    def create_listener(self,protocol, port, default_action, certificate='None'):
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


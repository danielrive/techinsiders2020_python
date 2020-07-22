import pulumi

import infra

if __name__ == '__main__':
    pulumi.export('vpc_id', infra.net_info['vpc_info'].id)
    pulumi.export('subnet_public_ids', infra.net_info['public_subnets'][0])
    pulumi.export('subnet_private_ids', infra.net_info['private_subnets'][0])
    pulumi.export('ALB_DNS', infra.create_alb['alb_dns'])
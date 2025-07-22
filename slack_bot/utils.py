import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError

def get_aws_session(service_name: str):
    env = os.getenv("ENV", "prod")  # 기본은 prod
    if env == "local":
        profile = os.getenv("AWS_PROFILE", "default")
        session = boto3.Session(profile_name=profile)
    else:
        session = boto3.Session()
    return session.client(service_name)

def get_security_groups_data():
    try:
        ec2 = get_aws_session('ec2')
        response = ec2.describe_security_groups()

        # 필요한 필드만 정리
        security_groups = [
            {
                "GroupId": sg["GroupId"],
                "GroupName": sg["GroupName"],
                "Description": sg["Description"],
                "VpcId": sg.get("VpcId"),
                "InboundRules": sg.get("IpPermissions", []),
                "OutboundRules": sg.get("IpPermissionsEgress", []),
            }
            for sg in response["SecurityGroups"]
        ]
        return security_groups, None  # 성공 시

    except (BotoCoreError, ClientError) as e:
        return None, str(e)  # 오류 시

def add_inbound_rule(data):
    try:
        ec2 = get_aws_session('ec2')
        ec2.authorize_security_group_ingress(
            GroupId=data['GroupId'],
            IpPermissions=[{
                'IpProtocol': data['IpProtocol'],
                'FromPort': int(data['FromPort']),
                'ToPort': int(data['ToPort']),
                'IpRanges': [{'CidrIp': data['CidrIp']}]
            }]
        )
        return True, None
    except (ClientError, BotoCoreError) as e:
        return False, str(e)


def remove_inbound_rule(data):
    try:
        ec2 = get_aws_session('ec2')
        ec2.revoke_security_group_ingress(
            GroupId=data['GroupId'],
            IpPermissions=[{
                'IpProtocol': data['IpProtocol'],
                'FromPort': int(data['FromPort']),
                'ToPort': int(data['ToPort']),
                'IpRanges': [{'CidrIp': data['CidrIp']}]
            }]
        )
        return True, None
    except (ClientError, BotoCoreError) as e:
        return False, str(e)
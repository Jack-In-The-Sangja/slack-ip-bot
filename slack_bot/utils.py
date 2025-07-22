import boto3
import os
from botocore.exceptions import BotoCoreError, ClientError

def get_aws_session(service_name: str):
    env = os.getenv("ENV", "prod")  # 기본은 prod
    region = os.getenv("AWS_REGION", "ap-northeast-2")  # 리전 환경변수 또는 기본값
    if env == "local":
        profile = os.getenv("AWS_PROFILE", "default")
        session = boto3.Session(profile_name=profile, region_name=region)
    else:
        session = boto3.Session(region_name=region)
    return session.client(service_name)

# 이하 동일
def get_security_groups_data():
    try:
        ec2 = get_aws_session('ec2')
        response = ec2.describe_security_groups()

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
        return security_groups, None

    except (BotoCoreError, ClientError) as e:
        return None, str(e)

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

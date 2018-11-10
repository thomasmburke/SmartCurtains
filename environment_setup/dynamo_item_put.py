import boto3
from botocore.exceptions import ClientError
import os
import json


def put_config_items():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('skill_config')
    configFilePath = os.path.join(os.path.dirname(__file__), 'response_config.json')
    configFile = open(configFilePath, 'r')
    configs = json.loads(configFile.read())
    for skillName in configs['skillNames']:
        item = {}
        item['skillName'] = skillName['skillName']
        item['config'] = str(json.dumps(skillName))
        try:
            table.put_item(Item=item)
        except ClientError as cE:
            print(cE)
            pass

if __name__=='__main__':
    put_config_items()

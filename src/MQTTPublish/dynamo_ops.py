import boto3
from botocore.exceptions import ClientError
import json


class DynamoOps:

    def __init__(self, skillName):
        self.configTable = boto3.resource('dynamodb').Table('skill_config')
        self.skillName = skillName

    def get_config(self): 
        skillConfig = json.loads(self.configTable.get_item(  
            Key={
                'skillName': self.skillName
            }
        )['Item']['config'])
        return skillConfig

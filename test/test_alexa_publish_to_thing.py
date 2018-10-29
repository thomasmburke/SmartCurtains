from context import src
from src.MQTTPublish.alexa_publish_to_thing import SkillHandler
import json

with open('../src/MQTTPublish/response_config.json') as f:
    responseConfig = json.load(f)
print(SkillHandler(event={'request': {'type': 'yumm'},'session': {'application': {'applicationId': 'tommy'}}},responseConfig=responseConfig).intentResponse)

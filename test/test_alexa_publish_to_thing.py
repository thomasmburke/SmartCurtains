from .context import src
from src.MQTTPublish.alexa_publish_to_thing import SkillHandler
import json
import pytest

# Get response config for all pytest fixtures
with open('../src/MQTTPublish/response_config.json') as f:
    responseConfig = json.load(f)

"""
SET ALL PYTEST FIXTURES
"""


@pytest.fixture
def launch_skill_handler():
    '''Returns a SkillHandler instance with a launch request event'''
    with open('json_requests/launch_request.json') as f:
        event = json.load(f)
    return SkillHandler(event=event, responseConfig=responseConfig)


@pytest.fixture
def stop_skill_handler():
    '''Returns a SkillHandler instance with a stop request event'''
    with open('json_requests/stop_request.json') as f:
        event = json.load(f)
    return SkillHandler(event=event, responseConfig=responseConfig)


@pytest.fixture
def assistance_skill_handler():
    '''Returns a SkillHandler instance with an assistance request event'''
    with open('json_requests/assistance_request.json') as f:
        event = json.load(f)
    return SkillHandler(event=event, responseConfig=responseConfig)


@pytest.fixture
def fallback_skill_handler():
    '''Returns a SkillHandler instance with a fallback request event'''
    with open('json_requests/fallback_request.json') as f:
        event = json.load(f)
    return SkillHandler(event=event, responseConfig=responseConfig)


@pytest.fixture
def curtain_close_skill_handler():
    '''Returns a SkillHandler instance with a curtain close request event'''
    with open('json_requests/alexa_curtain_intent.json') as f:
        event = json.load(f)
    return SkillHandler(event=event, responseConfig=responseConfig)


"""
BEGIN UNIT TESTS
"""

def test_skill_name(launch_skill_handler):
    assert launch_skill_handler.skillName == 'GPIOControl'
"""
TESTS TO MAKE:
- Test __init__: (give different skillIds, requestTypes)
    requestType
    skillName
    intentResponse
    curtainCmds
- Test alexa_publish_to_thing with several different events
- Test handle_skill for both launch and intent requestType
"""

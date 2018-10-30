from .context import src
from src.MQTTPublish.alexa_publish_to_thing import SkillHandler
import json
import pytest


jsonRequestsPath = 'alexa_json_messages/json_requests'
jsonResponsesPath = 'alexa_json_messages/json_responses'
# Get response config for all pytest fixtures
with open('../src/MQTTPublish/response_config.json') as f:
    responseConfig = json.load(f)
# Get sample launch response
with open('{}/launch_response.json'.format(jsonResponsesPath)) as f:
    launchResponse = json.load(f)


#################################
#                               #
#    SET ALL PYTEST FIXTURES    #
#                               #
#################################


@pytest.fixture
def launch_skill_handler():
    '''Returns a SkillHandler instance with a launch request event'''
    with open('{}/launch_request.json'.format(jsonRequestsPath)) as f:
        event = json.load(f)
    return SkillHandler(event=event, responseConfig=responseConfig)


@pytest.fixture
def stop_skill_handler():
    '''Returns a SkillHandler instance with a stop request event'''
    with open('{}/stop_request.json'.format(jsonRequestsPath)) as f:
        event = json.load(f)
    return SkillHandler(event=event, responseConfig=responseConfig)


@pytest.fixture
def assistance_skill_handler():
    '''Returns a SkillHandler instance with an assistance request event'''
    with open('{}/assistance_request.json'.format(jsonRequestsPath)) as f:
        event = json.load(f)
    return SkillHandler(event=event, responseConfig=responseConfig)


@pytest.fixture
def fallback_skill_handler():
    '''Returns a SkillHandler instance with a fallback request event'''
    with open('{}/fallback_request.json'.format(jsonRequestsPath)) as f:
        event = json.load(f)
    return SkillHandler(event=event, responseConfig=responseConfig)


@pytest.fixture
def invalid_skill_id_skill_handler():
    '''Returns a SkillHandler instance with a invalid skillId'''
    with open('{}/invalid_skill_id_request.json'.format(jsonRequestsPath)) as f:
        event = json.load(f)
    return SkillHandler(event=event, responseConfig=responseConfig)


@pytest.fixture
def curtain_close_skill_handler():
    '''Returns a SkillHandler instance with a curtain close request event'''
    with open('{}/curtain_close_request.json'.format(jsonRequestsPath)) as f:
        event = json.load(f)
    return SkillHandler(event=event, responseConfig=responseConfig)


#################################
#                               #
#     Other Key Declarations    #
#                               #
#################################

launchDict = {'outputSpeech': 'Hi, welcome to the raspberry pi alexa skill', 
    'repromptMessage': 'Please supply an appropriate pi command', 
    'cardText': 'Supply a command for the curtain', 
    'cardTitle': 'Curain Command', 
    'endSession': False}
curtainCloseDict = {'outputSpeech': 'You have chosen to close the curtain', 
    'repromptMessage': 'Do you want to adjust the curtain setting again?', 
    'cardText': 'You have chosen to close the curtain', 
    'cardTitle': 'Curtain Adjustment', 
    'endSession': True}


#################################
#                               #
#        BEGIN UNIT TESTS       #
#                               #
#################################

"""
Test __init__ settings
"""


def test_curtain_skill_name(invalid_skill_id_skill_handler):
    assert invalid_skill_id_skill_handler.skillName == 'GPIOControl'
    assert isinstance(invalid_skill_id_skill_handler.skillName, str)


def test_invalid_skill_name(launch_skill_handler):
    assert launch_skill_handler.skillName == 'GPIOControl'
    assert isinstance(launch_skill_handler.skillName, str)


def test_intent_request_type(curtain_close_skill_handler, stop_skill_handler):
    assert curtain_close_skill_handler.requestType == 'IntentRequest'
    assert stop_skill_handler.requestType == 'IntentRequest'
    assert isinstance(curtain_close_skill_handler.requestType, str)
    assert isinstance(stop_skill_handler.requestType, str)


def test_launch_request_type(launch_skill_handler):
    assert launch_skill_handler.requestType == 'LaunchRequest'
    assert isinstance(launch_skill_handler.requestType, str)


def test_curtain_commands(launch_skill_handler):
    assert launch_skill_handler.curtainCmds == ['open', 'close', 'shut']
    assert isinstance(launch_skill_handler.curtainCmds, list)


def test_intent_response_with_invalid_skill_id(invalid_skill_id_skill_handler):
    assert invalid_skill_id_skill_handler.intentResponse == responseConfig['GPIOControl']
    assert isinstance(invalid_skill_id_skill_handler.intentResponse, dict)


def test_intent_response_with_curtain_skill_id(curtain_close_skill_handler):
    assert curtain_close_skill_handler.intentResponse == responseConfig['GPIOControl']
    assert isinstance(curtain_close_skill_handler.intentResponse, dict)

"""
Test SkillHandler methods
"""

def test_launch_request_handle_skill(launch_skill_handler):
    assert launch_skill_handler.handle_skill() == launchDict
    assert isinstance(launch_skill_handler.handle_skill(), dict)


def test_intent_request_handle_skill(curtain_close_skill_handler):
    assert curtain_close_skill_handler.handle_skill() == curtainCloseDict
    assert isinstance(curtain_close_skill_handler.handle_skill(), dict)


"""
TESTS TO MAKE:
- Test alexa_publish_to_thing with several different events
- Test handle_skill for both launch and intent requestType
"""

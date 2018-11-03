from .context import src
from src.MQTTPublish.alexa_publish_to_thing import SkillHandler
import json
import pytest
from unittest.mock import patch, mock_open


jsonRequestsPath = 'alexa_json_messages/json_requests'
jsonResponsesPath = 'alexa_json_messages/json_responses'
# Get response config for all pytest fixtures
with open('../src/MQTTPublish/response_config.json') as f:
    responseConfig = json.load(f)
# Get sample launch response
with open('{}/launch_response.json'.format(jsonResponsesPath)) as f:
    launchResponse = json.load(f)['body']
# Sample event for alexa_publish_to_thing
with open('{}/launch_request.json'.format(jsonRequestsPath)) as f:
    alexaEvent = json.load(f)


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
    yield SkillHandler(event=event, responseConfig=responseConfig)


@pytest.fixture
def session_ended_skill_handler():
    '''Returns a SkillHandler instance with a sessionEnded request event'''
    with open('{}/session_ended_request.json'.format(jsonRequestsPath)) as f:
        event = json.load(f)
    yield SkillHandler(event=event, responseConfig=responseConfig)


@pytest.fixture
def stop_skill_handler():
    '''Returns a SkillHandler instance with a stop request event'''
    with open('{}/stop_request.json'.format(jsonRequestsPath)) as f:
        event = json.load(f)
    yield SkillHandler(event=event, responseConfig=responseConfig)


@pytest.fixture
def cancel_skill_handler():
    '''Returns a SkillHandler instance with a cancel request event'''
    with open('{}/cancel_request.json'.format(jsonRequestsPath)) as f:
        event = json.load(f)
    yield SkillHandler(event=event, responseConfig=responseConfig)


@pytest.fixture
def assistance_skill_handler():
    '''Returns a SkillHandler instance with an assistance request event'''
    with open('{}/assistance_request.json'.format(jsonRequestsPath)) as f:
        event = json.load(f)
    yield SkillHandler(event=event, responseConfig=responseConfig)


@pytest.fixture
def fallback_skill_handler():
    '''Returns a SkillHandler instance with a fallback request event'''
    with open('{}/fallback_request.json'.format(jsonRequestsPath)) as f:
        event = json.load(f)
    yield SkillHandler(event=event, responseConfig=responseConfig)


@pytest.fixture
def invalid_skill_id_skill_handler():
    '''Returns a SkillHandler instance with a invalid skillId'''
    with open('{}/invalid_skill_id_request.json'.format(jsonRequestsPath)) as f:
        event = json.load(f)
    yield SkillHandler(event=event, responseConfig=responseConfig)


@pytest.fixture(scope='function')
def curtain_open_skill_handler():
    '''Returns a SkillHandler instance with a curtain open request event'''
    with open('{}/curtain_open_request.json'.format(jsonRequestsPath)) as f:
        event = json.load(f)
    curtainOpen = SkillHandler(event=event, responseConfig=responseConfig)
    yield curtainOpen


@pytest.fixture(scope='function')
def curtain_close_skill_handler():
    '''Returns a SkillHandler instance with a curtain close request event'''
    with open('{}/curtain_close_request.json'.format(jsonRequestsPath)) as f:
        event = json.load(f)
    curtainClose = SkillHandler(event=event, responseConfig=responseConfig)
    yield curtainClose


@pytest.fixture
def invalid_curtain_intent_skill_handler():
    '''Returns a SkillHandler instance with a invalid curtain intent request event'''
    with open('{}/invalid_curtain_intent_request.json'.format(jsonRequestsPath)) as f:
        event = json.load(f)
    yield SkillHandler(event=event, responseConfig=responseConfig)


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
curtainOpenDict = {'outputSpeech': 'You have chosen to open the curtain', 
    'repromptMessage': 'Do you want to adjust the curtain setting again?', 
    'cardText': 'You have chosen to open the curtain', 
    'cardTitle': 'Curtain Adjustment', 
    'endSession': True}
invalidCurtainIntentDict = {
    "outputSpeech": "plow is a curtain command not supported by the raspberry pi",
    "repromptMessage": "Do you want to perform an action on the curtains?",
    "cardText": "plow is a curtain command not supported by the raspberry pi",
    "cardTitle": "Invalid curtain command",
    "endSession": True
}
stopDict = {
    "outputSpeech": "Thank you. Bye!",
    "repromptMessage": "",
    "cardText": "Bye.",
    "cardTitle": "Bye Bye.",
    "endSession": True
}
assistanceDict = {
    "outputSpeech": "You can choose among the following curtain commands open,close,shut",
    "repromptMessage": "Do you want to perform another curtain comand?",
    "cardText": "You have asked for help.",
    "cardTitle": "HELP",
    "endSession": False
}
fallbackDict = {
    "outputSpeech": "I can not help you with that, try rephrasing the question or ask for help by saying HELP.",
    "repromptMessage": "Do you want to perform another curtain comand?",
    "cardText": "You have given an invalid command",
    "cardTitle": "Invalid command",
    "endSession": False
}


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


def test_intent_response_with_curtain_close_skill_id(curtain_close_skill_handler):
    assert curtain_close_skill_handler.intentResponse == responseConfig['GPIOControl']
    assert isinstance(curtain_close_skill_handler.intentResponse, dict)


def test_intent_response_with_curtain_open_skill_id(curtain_open_skill_handler):
    assert curtain_open_skill_handler.intentResponse == responseConfig['GPIOControl']
    assert isinstance(curtain_open_skill_handler.intentResponse, dict)

"""
Test SkillHandler methods
"""

# HANDLE_SKILL()
def test_launch_request_handle_skill(launch_skill_handler):
    assert launch_skill_handler.handle_skill() == launchDict
    assert isinstance(launch_skill_handler.handle_skill(), dict)


def test_intent_request_handle_skill(curtain_close_skill_handler):
    assert curtain_close_skill_handler.handle_skill() == curtainCloseDict
    assert isinstance(curtain_close_skill_handler.handle_skill(), dict)

def test_open_intent_request_handle_skill(curtain_open_skill_handler):
    assert curtain_open_skill_handler.handle_skill() == curtainOpenDict
    assert isinstance(curtain_open_skill_handler.handle_skill(), dict)


def test_session_ended_request_handle_skill(session_ended_skill_handler):
    assert session_ended_skill_handler.handle_skill() == stopDict
    assert isinstance(session_ended_skill_handler.handle_skill(), dict)

# LAUNCH_HANDLER()
def test_launch_handler(launch_skill_handler):
    assert launch_skill_handler.launch_handler() == launchDict
    assert isinstance(launch_skill_handler.launch_handler(), dict)

# INTENT_HANDLER()
def test_intent_handler_with_open_curtain_intent(curtain_open_skill_handler):
    assert curtain_open_skill_handler.intent_handler() == curtainOpenDict
    assert isinstance(curtain_open_skill_handler.intent_handler(), dict)


def test_intent_handler_with_close_curtain_intent(curtain_close_skill_handler):
    assert curtain_close_skill_handler.intent_handler() == curtainCloseDict
    assert isinstance(curtain_close_skill_handler.intent_handler(), dict)


def test_intent_handler_with_stop_or_cancel_intent(stop_skill_handler,cancel_skill_handler):
    assert stop_skill_handler.intent_handler() == stopDict
    assert cancel_skill_handler.intent_handler() == stopDict
    assert isinstance(stop_skill_handler.intent_handler(), dict)
    assert isinstance(cancel_skill_handler.intent_handler(), dict)


def test_intent_handler_with_assistance_intent(assistance_skill_handler):
    assert assistance_skill_handler.intent_handler() == assistanceDict
    assert isinstance(assistance_skill_handler.intent_handler(), dict)


def test_intent_handler_with_fallback_intent(fallback_skill_handler):
    assert fallback_skill_handler.intent_handler() == fallbackDict
    assert isinstance(fallback_skill_handler.intent_handler(), dict)

# CURTAIN_CONTROL()
def test_curtain_control_with_open_command(curtain_open_skill_handler):
    assert curtain_open_skill_handler.curtain_control() == curtainOpenDict
    assert isinstance(curtain_open_skill_handler.curtain_control(), dict)


def test_curtain_control_with_close_command(curtain_close_skill_handler):
    assert curtain_close_skill_handler.curtain_control() == curtainCloseDict
    assert isinstance(curtain_close_skill_handler.curtain_control(), dict)


def test_curtain_control_with_close_command(invalid_curtain_intent_skill_handler):
    assert invalid_curtain_intent_skill_handler.curtain_control() == invalidCurtainIntentDict
    assert isinstance(invalid_curtain_intent_skill_handler.curtain_control(), dict)

# STOP()
def test_stop(stop_skill_handler):
    assert stop_skill_handler.stop() == stopDict
    assert isinstance(stop_skill_handler.stop(), dict)

# ASSISTANCE()
def test_assistance(assistance_skill_handler):
    assert assistance_skill_handler.assistance() == assistanceDict
    assert isinstance(assistance_skill_handler.assistance(), dict)

# FALLBACK()
def test_fallback(fallback_skill_handler):
    assert fallback_skill_handler.fallback() == fallbackDict
    assert isinstance(fallback_skill_handler.fallback(), dict)

# BUILD_RESPONSE
def test_build_response(launch_skill_handler):
    assert launch_skill_handler.build_response(response=launchDict) == launchResponse
    assert isinstance(launch_skill_handler.build_response(response=launchDict), dict)

# BUILD_OUTPUT_SPEECH
def test_build_output_speech(launch_skill_handler):
    outputSpeech = 'outputSpeech'
    assert launch_skill_handler.build_output_speech(outputSpeech) == {'type': 'PlainText', 'text': outputSpeech}
    assert isinstance(launch_skill_handler.build_output_speech(outputSpeech), dict)

# BUILD_CARD
def test_build_card(launch_skill_handler):
    cardTitle = 'Title'
    cardText = 'Text'
    assert launch_skill_handler.build_card(cardText=cardText, cardTitle=cardTitle) == {'type': 'Simple', 'title': cardTitle, 'content': cardText}
    assert isinstance(launch_skill_handler.build_card(cardText=cardText, cardTitle=cardTitle), dict)

#TODO: finish this mocking exercise
# ALEXA_PUBLISH_TO_THING
def test_alexa_publish_to_thing(event=alexaEvent,context=None,filename='response_config.json'):
    with patch('builtins.open', mock_open(read_data="data")) as mockFile:
        assert open(filename).read() == 'data'
        mockFile.assert_called_with(filename)

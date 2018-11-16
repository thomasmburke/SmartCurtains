import json
import logging
from dynamo_ops import DynamoOps
from iot_ops import IoTOps
from botocore.exceptions import ClientError

# Initialize logger for CloudWatch logs
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def alexa_skill_handler(event, context):
    """
    Description: This is lambda's handler function that will leverage the
    SkillHandler class to interpret a request from alexa and return the 
    appropriate response
    """
    # Gather skillName based off of skillId from dynamo
    try:
        # Query dynamo for skillName based off of skillId
        skillName = DynamoOps(skillName='skillIds').get_config()['ids'][event['session']['application']['applicationId']]
    except ClientError as e:
        logger.error('got unexpected skillID: {}'.format(event['session']['application']['applicationId']))
        skillName = 'CurtainControl'

    skillHandler = SkillHandler(event=event, skillName=skillName)
    response = skillHandler.handle_skill()
    return skillHandler.build_response(response=response)


class SkillHandler(DynamoOps, IoTOps):
    """
    Description: The SkillHandler class is used to inspect a JSON Request
    from an alexa skill and determine an appropriate response to send back.
    The skill handler will check the type of response and use it as fodder
    to either prompt the user again or to coordinate a command

    Params: DICT event - a JSON request from an alexa custom skill detailing
    an action/response to be taken
        STRING skillName - the name of the skill to index dynamo with
    """
    def __init__(self, event, skillName):
        self.event = event
        self.requestType = event['request']['type']
        self.skillName = skillName
        DynamoOps.__init__(self, skillName=skillName)
        self.skillConfig = super().get_config()
        IoTOps.__init__(self, iotConfig=self.skillConfig['iotConfig'])

    def handle_skill(self):
        """
        Description: The handle_skill is a method that will act as the brains
        of the class. Administering necessary commands to send MQTT messages 
        to the raspberry pi and proper JSON back to alexa

        Return: DICT response - a JSON response to instruct alexa on what to 
        do/say next
        """
        logger.info('got event: {}'.format(self.event))
        requestTypeFunc = {
            'LaunchRequest': self.launch_handler,
            'IntentRequest': self.intent_handler,
            }
        if self.requestType in requestTypeFunc:
            logger.info('received a {} requestType'.format(self.requestType))
            response = requestTypeFunc[self.requestType]()
            return response
        else:
            logging.info('Session Ended.')
            return self.stop()

    def launch_handler(self):
        """
        Description: Given a user calls the Invocation name with no command,
        this function will greet the user to the custom skill.

        Return: DICT - response gathered from response_config.json
        """
        return self.skillConfig['responses']['launchResponse']

    def intent_handler(self):
        """
        Description: The intent_handler(event) function handles the Intent Request. 
        Since we have a few different intents in our skill, we need to 
        configure what this function will do upon receiving a particular 
        intent. This can be done by introducing the functions which handle 
        each of the intents.

        Return: DICT - response gathered from function it decides
        """
        # Create function dictionary based on intent name
        intentFunc = {
                'CurtainControl': self.curtain_control,
                'AMAZON.StopIntent': self.stop,
                'AMAZON.CancelIntent': self.stop,
                'AMAZON.HelpIntent': self.assistance,
                'AMAZON.FallbackIntent': self.fallback
                }
        # Gather the name of the intent sent from alexa
        intentName = self.event['request']['intent']['name']
        logger.info('Received the following intent: {}'.format(intentName))
        # Call appropriate function to handle intent
        if intentName in intentFunc:
            response = intentFunc[intentName]()
        else:
            response = self.stop() 
        return response

    def curtain_control(self):
        """
        Description: Analyze intent response. If valid slot value for -status- is 
        given then an appropriate MQTT message will be sent to the associated AWS
        IoT thing. If invalid value is given the user will be prompted to try 
        another action phrase.

        Return: DICT - curtainResponse gathered from response_config.json
        based on whether or not the command was valid
        """
        # Retrieve the curtain command supplied by the end user
        curtainCmd = self.event['request']['intent']['slots']['status']['value']
        curtainDirection = self.event['request']['intent']['slots']['direction'].get('value')
        # Check to see if user supplied curtain command is in valid command list
        if curtainCmd in self.skillConfig['slots']['status']:
            # Valid Status and Direction Request
            if curtainDirection in self.skillConfig['slots']['direction']:
                curtainSpeech = 'left and right' if curtainDirection == 'both' else curtainDirection
                curtainResponse = self.insert_into_response(self.skillConfig['responses']['validStatusDirectionIntentResponse'], curtainCmd, curtainSpeech)
                curtainCmd = 'open' if curtainCmd in self.skillConfig['commands']['openCommands'] else 'close'
                super().publish_mqtt_message(status=curtainCmd, direction=curtainDirection)
            # Invalid Direction Request
            elif curtainDirection is not None and curtainDirection not in self.skillConfig['slots']['direction']:
                logger.info('curtain command: {} supplied by end user is invalid'.format(curtainDirection))
                curtainResponse = self.insert_into_response(self.skillConfig['responses']['invalidIntentResponse'], curtainDirection)
            # Valid Status Request
            else:
                logger.info('curtain command: {} supplied by end user is valid'.format(curtainCmd))
                curtainResponse = self.insert_into_response(self.skillConfig['responses']['validStatusIntentResponse'], curtainCmd)
                curtainCmd = 'open' if curtainCmd in self.skillConfig['commands']['openCommands'] else 'close'
                super().publish_mqtt_message(status=curtainCmd, direction='both')
        # Invalid Status Request
        else:
            logger.info('curtain command: {} supplied by end user is invalid'.format(curtainCmd))
            curtainResponse = self.insert_into_response(self.skillConfig['responses']['invalidIntentResponse'], curtainCmd)
        return curtainResponse

    def insert_into_response(self, response, *responseInputs):
        """
        Summary: takes in a response dictionary and inserts skill specific
        inputs if value is a string

        Params: response DICT - this is the response to be modified
            *responseInputs LIST - this is the list of inputs to be inserted
            into the response

        Return: response DICT - the modified dictionary
        """
        for k, v in response.items():
            response[k] = v.format(*responseInputs) if isinstance(v,str) else v
        return response

    def stop(self):
        """
        Description: Used to build exit response for alexa skill.

        Return: DICT - response gathered from response_config.json
        """
        logger.info('stopping alexa skill...')
        return self.skillConfig['responses']['stopResponse']
        
    def assistance(self):
        """
        Description: Used to help user provide a valid command. 
        This is triggered when the end user says HELP.

        Return: DICT - assistanceResponse gathered from response_config.json with curtain commands
        """
        logger.info('assistance method was called due to user saying HELP')
        assistanceResponse = self.insert_into_response(self.skillConfig['responses']['assistanceResponse'],
                ', '.join(self.skillConfig['slots']['status']))
        return assistanceResponse

    def fallback(self):
        """
        Description: Used to handle any unexpected utterances given when the
        alexa hears the invocation name paired with an invalid command.

        Return: DICT - response gathered from response_config.json
        """
        logger.info('fallback method was called due to unexpected utterance after \
                hearing the invocation name')
        return self.skillConfig['responses']['fallbackResponse']

    def build_response(self, response): 
        """
        Description: The response of our Lambda function should be in a json format. 
        That is why in this part of the code we define the functions which 
        will build the response in the requested format. These functions
        are used by both the intent handlers and the request handlers to 
        build the output.

        Params: 
        DICT response which holds the following args
            STRING outputSpeech - What alexa will say back to the user
            STRING cardText - text to display on alex app
            STRING cardTitle - text to display as the response title on mobile app
            STRING repromptMessage - Message alexa will say while waiting for next input
            BOOL endSession - determines whether the conversation with alexa is over

        Return: DICT formattedResponse - a JSON response with structure alexa skill anticipates
        """
        # Begin building JSON response for alexa skill
        logger.info('Building JSON formattedResponse for alexa skill...')
        formattedResponse = {}
        formattedResponse['version'] = '1.0'
        formattedResponse['response'] = {
                'outputSpeech': self.build_output_speech(outputSpeech=response['outputSpeech']),
                'card': self.build_card(cardText=response['cardText'], cardTitle=response['cardTitle']),
                'reprompt': {'outputSpeech': self.build_output_speech(outputSpeech=response['repromptMessage'])},
                'shouldEndSession': response['endSession']}
        logger.info('JSON formattedResponse to return to alexa skill={}'.format(formattedResponse))
        return formattedResponse

    def build_output_speech(self, outputSpeech):
        """
        Description: Used to build output speech portion of JSON sent to alexa skill

        Params: STRING outputSpeech - text for alexa to speak back to the user
        
        Return: DICT speechDict - portion of JSON response to inform alexa what to
        say back to the end user
        """
        logger.info('building outputSpeech to say back to the user...')
        speechDict = {'type': 'PlainText', 'text': outputSpeech}
        return speechDict

    def build_card(self, cardText, cardTitle):
        """
        Description: Used to build title and text display for mobile app (card)

        Params: STRING cardText - body of phone app message
        STRING cardTitle - title of phone app message

        Return: DICT card - portion of JSON response to be sent to alexa mobile app
        """
        logger.info('building card to display on users mobile app...')
        card = {'type': 'Simple', 'title': cardTitle, 'content': cardText}
        return card

if __name__=='__main__':
    with open('direction_status_intent.json') as intentRequest:
        event = json.load(intentRequest)
    print(alexa_skill_handler(event=event, context=None))

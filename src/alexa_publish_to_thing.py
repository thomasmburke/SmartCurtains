import json
import boto3
import logging

# TODO: get rid of remprompt where endSession is true (in json)
# TODO: make SkillHandler a virtual class and Curtain child class (maybe not..)

# Initialize logger for CloudWatch logs
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def alexa_publish_to_thing(event, context):
    """
    Description: This is lambda's handler function that will leverage the
    SkillHandler class to interpret a request from alexa and return the 
    appropriate response
    """
    # Gather response config
    with open('response_config.json') as f:
        responseConfig = json.load(f)
    return SkillHandler(event=event, responseConfig=responseConfig).handle_skill()


class SkillHandler:
    """
    Description: The SkillHandler class is used to inspect a JSON Request
    from an alexa skill and determine an appropriate response to send back.
    The skill handler will check the type of response and use it as fodder
    to either prompt the user again or to coordinate a command

    Params: DICT event - a JSON request from an alexa custom skill detailing
    an action/response to be taken
    """
    def __init__(self, event, responseConfig):
        self.event = event
        self.requestType = event['request']['type']
        self.curtainCmds = ['open', 'close', 'shut']
        try:
            self.skillName = responseConfig['skillNames'][event['session']['application']['applicationId']]
        except:
            logger.error('got unexpected skillID: {}'.format(event['session']['application']['applicationId']))
            self.skillName = 'GPIOControl'
        self.intentResponse = responseConfig[self.skillName]

    def handle_skill(self):
        """
        Description: The handle_skill is a method that will act as the brains
        of the class. Administering necessary commands to send MQTT messages 
        to the raspberry pi and proper JSON back to alexa

        Params: DICT event - a JSON request sent by alexa

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
            return requestTypeFunc[self.requestType](self.event)
        else:
            logging.info('Session Ended.')
            return

    def mqtt_message(self):
        """
        Description: Send MQTT message to raspberry pi

        Return: TBD
        """
        # Initialize iot client to publish messages to a IoT thing
        logger.info('connecting to iot-data module...')
        client = boto3.client('iot-data', region_name='us-east-1')
        # Set MQTT variables
        topic = 'raspberrypi3'
        QoS = 1
        # Publish a MQTT message to a topic for our thing to ingest
        logger.info('publishing MQTT message to topic: {}'.format(topic))
        client.publish(
            topic=topic,  # '$aws/things/pi/shadow/update',
            qos=QoS,
            payload=json.dumps({'foo': 'bar'})
        )

    def launch_handler(self, event):
        """
        Description: Given a user calls the Invocation name with no command,
        this function will greet the user to the custom skill.

        Params: event - a JSON passed by alexa

        Return: TBD
        """
        return self.build_response(response=self.intentResponse['launchResponse'])

    def intent_handler(self, event):
        """
        Description: The intent_handler(event) function handles the Intent Request. 
        Since we have a few different intents in our skill, we need to 
        configure what this function will do upon receiving a particular 
        intent. This can be done by introducing the functions which handle 
        each of the intents.

        Params: event - a JSON passed by alexa

        Return: TBD
        """
        # Create function dictionary based on intent name
        intentFunc = {
                'GPIOControl': self.curtain_control,
                'AMAZON.StopIntent': self.stop,
                'AMAZON.CancelIntent': self.stop,
                'AMAZON.HelpIntent': self.assistance,
                'AMAZON.FallbackIntent': self.fallback
                }
        # Gather the name of the intent sent from alexa
        intentName = event['request']['intent']['name']
        logger.info('Received the following intent: {}'.format(intentName))
        if intentName in intentFunc:
            return intentFunc[intentName](event)
        else:
            return self.stop(event) 

    def curtain_control(self, event):
        """
        Description: Analyze intent response. If valid slot value for -status- is 
        given then an appropriate MQTT message will be sent to the associated AWS
        IoT thing. If invalid value is given the user will be prompted to try 
        another action phrase.

        Params: event - a JSON passed by alexa

        Return: TBD
        """
        # TODO: see if we can call alexa for appropriate slot values / store in dynamodb
        # Retrieve the curtain command supplied by the end user
        curtainCmd = event['request']['intent']['slots']['status']['value']
        # Check to see if user supplied curtain command is in valid command list
        if curtainCmd in self.curtainCmds:
            logger.info('curtain command: {} supplied by end user is valid'.format(curtainCmd))
            curtainResponse = self.intentResponse['validIntentResponse']
            for k, v in curtainResponse.items():
                curtainResponse[k] = v.format(curtainCmd) if isinstance(v,str) else v
            return self.build_response(response=curtainResponse)
        else:
            logger.info('curtain command: {} supplied by end user is invalid'.format(curtainCmd))
            curtainResponse = self.intentResponse['invalidIntentResponse']
            for k, v in curtainResponse.items():
                curtainResponse[k] = v.format(curtainCmd)
            return self.build_response(response=curtainResponse)

    def stop(self, event):
        """
        Description: Used to build exit response for alexa skill.
        
        Params: event - JSON passed from alexa skill

        Return: TBD
        """
        logger.info('stopping alexa skill...')
        return self.build_response(response=self.intentResponse['stopResponse'])
        
    def assistance(self, event):
        """
        Description: Used to help user provide a valid command. 
        This is triggered when the end user says HELP.

        Params: event - JSON passed from alexa skill

        Return: TBD
        """
        logger.info('assistance method was called due to user saying HELP')
        assistanceResponse = self.intentResponse['assistanceResponse']
        for k, v in assistanceResponse.items():
            assistanceResponse[k] = v.format(','.join(map(str, self.curtainCmds))) if isinstance(v, str) else v
        return self.build_response(response=assistanceResponse)

    def fallback(self, event):
        """
        Description: Used to handle any unexpected utterances given when the
        alexa hears the invocation name paired with an invalid command.

        Params: event - JSON passed from alexa skill

        Return: TBD
        """
        logger.info('fallback method was called due to unexpected utterance after \
                hearing the invocation name')
        return self.build_response(response=self.intentResponse['fallbackResponse'])

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
    with open('intent_request.json') as intentRequest:
        event = json.load(intentRequest)
    print(alexa_publish_to_thing(event=event, context=None))

import json
import boto3
import logging

#TODO: Turn into a skill_handler class
#TODO: Think if it makes sense to put all these responses in dynamodb

# Initialize logger for CloudWatch logs
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def alexa_publish_to_thing(event, context):
    """
    Description: Here we define our Lambda function and configure what it does
    when an event with a Launch, Intent and Session End Requests are sent.
    The Lambda function responses to an event carrying a particular
    Request are handled by functions such as launch_handler(event) and
    intent_handler(event).
    """
    logger.info('got event: '.format(event))
    # Initialize iot client to publish messages to a IoT thing
    logger.info('connecting to iot-data module...')
    client = boto3.client('iot-data', region_name='us-east-1')
    # Set MQTT variables
    topic = 'raspberrypi3'
    QoS = 1
    # Publish a MQTT message to a topic for our thing to ingest
    logger.info('publishing MQTT message to topic: {}'.format(topic))
    client.publish(
        topic=topic,#'$aws/things/pi/shadow/update',
        qos=QoS,
        payload=json.dumps({'foo':'bar'})
    )
    # Gather request type and kick off appropriate function
    requestType = event['request']['type']
    requestTypeFunc = {
            'LaunchRequest': launch_handler,
            'IntentRequest': intent_handler,
            }
    if requestType in requestTypeFunc:
        logger.info('received a {} requestType'.format(requestType))
        requestTypeFunc[requestType](event)
    else:
        logging.info('Session Ended.')


def launch_handler(event):
    """
    Description: Given a user calls the Invocation name with no command, this
    function will greet the user to the custom skill.

    Params: event - a JSON passed by alexa

    Return: TBD
    """
    launchMessage = "Hi, welcome to the raspberry pi alexa skill"
    repromptMessage = "Please supply an appropriate pi command?"
    cardText = "Pick pin and status."
    cardTitle = "Choose a pin and status."
    return build_response(outputSpeech=launchMessage, cardText=cardText,
            cardTitle=cardTitle, repromptMessage=repromptMessage, endSession=False)


def intent_handler(event):
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
            'GPIOControl': curtain_control,
            'AMAZON.StopIntent': stop,
            'AMAZON.CancelIntent': stop,
            'AMAZON.HelpIntent': assistance,
            'AMAZON.FallbackIntent': fallback
            }
    # Gather the name of the intent sent from alexa
    intentName = event['request']['intent']['name']
    logger.info('Received the following intent: {}'.format(intentName))
    if intentName in intentFunc:
        return intentFunc[intentName](event)
    else:
        return stop(event) 


def curtain_control(event):
    """
    Description: Analyze intent response. If valid slot value for -status- is 
    given then an appropriate MQTT message will be sent to the associated AWS
    IoT thing. If invalid value is given the user will be prompted to try 
    another action phrase.

    Params: event - a JSON passed by alexa

    Return: TBD
    """
    # List of appropriate curtain commands
    #TODO: see if we can call alexa for appropriate slot values / store in dynamodb
    #TODO: this list should be stored in skill_handler __init__
    curtainCmds = ['open', 'close', 'shut']
    # Retrieve the curtain command supplied by the end user
    curtainCmd = event['request']['intent']['slots']['status']['value']
    # Check to see if user supplied curtain command is in valid command list
    if curtainCmd in curtainCmds:
        logger.info('curtain command: {} supplied by end user is valid'.format(curtainCmd))
        confirmationMessage = 'You have chosen to {} the curtain'.format(curtainCmd)
        repromptMessage = 'Do you want to adjust the curtain setting again?'
        cardText = confirmationMessage
        cardTitle = confirmationMessage
        return build_response(outputSpeech=confirmationMessage, cardText=cardText,
                cardTitle=cardTitle, repromptMessage=repromptMessage, endSession=False)
    else:
        logger.info('curtain command: {} supplied by end user is invalid'.format(curtainCmd))
        invalidCmd = '{} is a curtain command not supported by the raspberry pi'.format(curtainCmd)
        repromptMessage = 'Do you want to perform an action on the curtains?'
        cardText = '{} is a curtain command not supported by the raspberry pi'.format(curtainCmd)
        cardTitle = 'Invalid curtain command.'
        return build_response(outputSpeech=invalidCmd, cardText=cardText,
                cardTitle=cardTitle, repromptMessage=repromptMessage, endSession=False)
        
        
def stop(event):
    """
    Description: Used to build exit response for alexa skill.
    
    Params: event - JSON passed from alexa skill

    Return: TBD
    """
    logger.info('stopping alexa skill...')
    stopMessage = 'Thank you. Bye!'
    repromptMessage = ''
    cardText = 'Bye.'
    cardTitle = 'Bye Bye.'
    return build_response(outputSpeech=stopMessage, cardText=cardText,
            cardTitle=cardTitle, repromptMessage=repromptMessage, endSession=True)
    
    
def assistance(event):
    """
    Description: Used to help user provide a valid command. 
    This is triggered when the end user says HELP.

    Params: event - JSON passed from alexa skill

    Return: TBD
    """
    #assistanceMessage = "You can choose among these players: " + ', '.join(map(str, Player_LIST)) + ". Be sure to use the full name when asking about the player."
    #TODO: Reference valid curtain commands once it exists within the __init__
    logger.info('assistance method was called due to user saying HELP')
    assistanceMessage = 'This is the assistance message'
    repromptMessage = 'Do you want to perform another curtain comand?'
    cardText = 'You have asked for help.'
    cardTitle = 'Help'
    return build_response(outputSpeech=assistanceMessage, cardText=cardText,
            cardTitle=cardTitle, repromptMessage=repromptMessage, endSession=False)

def fallback(event):
    """
    Description: Used to handle any unexpected utterances given when the
    alexa hears the invocation name paired with an invalid command.

    Params: event - JSON passed from alexa skill

    Return: TBD
    """
    logger.info('fallback method was called due to unexpected utterance after \
            hearing the invocation name')
    fallbackMessage = 'I can not help you with that, try rephrasing the question or ask for help by saying HELP.'
    repromptMessage = 'Do you want to perform another curtain command?'
    cardText = 'You have asked a wrong question.'
    cardTitle = 'Wrong question.'
    return build_response(outputSpeech=fallbackMessage, cardText=cardText,
            cardTitle=cardTitle, repromptMessage=repromptMessage, endSession=False)



def build_response(outputSpeech, cardText, cardTitle, repromptMessage, endSession): 
    """
    Description: The response of our Lambda function should be in a json format. 
    That is why in this part of the code we define the functions which 
    will build the response in the requested format. These functions
    are used by both the intent handlers and the request handlers to 
    build the output.

    Params: STRING outputSpeech - What alexa will say back to the user
    STRING cardText - text to display on alex app
    STRING cardTitle - text to display as the response title on mobile app
    STRING repromptMessage - Message alexa will say while waiting for next input
    BOOL endSession - determines whether the conversation with alexa is over

    Return: DICT response - a JSON response with structure alexa skill anticipates
    """
    # Begin building JSON response for alexa skill
    logger.info('Building JSON response for alexa skill...')
    response = {}
    response['version'] = '1.0'
    response['response'] = {
            'outputSpeech': build_output_speech(outputSpeech=outputSpeech),
            'card': build_card(cardText=cardText, cardTitle=cardTitle),
            'reprompt': {'outputSpeech':build_output_speech(outputSpeech=repromptMessage)},
            'shouldEndSession': endSession}
    logger.info('JSON response to return to alexa skill={}'.format(response))
    return response


def build_output_speech(outputSpeech):
    """
    Description: Used to build output speech portion of JSON sent to alexa skill

    Params: STRING outputSpeech - text for alexa to speak back to the user
    
    Return: DICT speechDict - portion of JSON response to inform alexa what to
    say back to the end user
    """
    logger.info('building outputSpeech to say back to the user...')
    speechDict = {'type': 'PlainText','text': outputSpeech}
    return speechDict


def build_card(cardText, cardTitle):
    """
    Description: Used to build title and text display for mobile app (card)

    Params: STRING cardText - body of phone app message
    STRING cardTitle - title of phone app message

    Return: DICT card - portion of JSON response to be sent to alexa mobile app
    """
    logger.info('building card to display on users mobile app...')
    card = {'type': 'Simple', 'title': cardTitle, 'cardText': cardText}
    return card

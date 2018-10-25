import json
import boto3
import logging

#TODO: Turn into a skill_handler class

# Initialize logger for CloudWatch logs
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def alexa_publish_to_thing(event, context):
    """
    Description: Here we define our Lambda function and configure what it does
    when an event with a Launch, Intent and Session End Requests are sent.
    The Lambda function responses to an event carrying a particular
    Request are handled by functions such as on_launch(event) and
    intent_scheme(event).
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
            'LaunchRequest': on_launch,
            'IntentRequest': intent_scheme,
            }
    if requestType in requestTypeFunc:
        requestTypeFunc[requestType](event)
    else:
        logging.info('Session Ended.')


def on_launch(event):
    launchMessage = "Hi, welcome to the raspberry pi alexa skill"
    repromptMessage = "Please supply an appropriate pi command?"
    cardText = "Pick pin and status."
    cardTitle = "Choose a pin and status."
    return output_json_builder_with_reprompt_and_card(launchMessage, cardText, cardTitle, repromptMessage, False)


def intent_scheme(event):
    """
    Description: The intent_scheme(event) function handles the Intent Request. 
    Since we have a few different intents in our skill, we need to 
    configure what this function will do upon receiving a particular 
    intent. This can be done by introducing the functions which handle 
    each of the intents.

    Params: event - a JSON passed by alexa

    Return: function - probably will change this...
    """
    # Create function dictionary based on intent name
    intentFunc ={
            'GPIOControl': gpio_control,
            'AMAZON.StopIntent': stop,
            'AMAZON.CancelIntent': stop,
            'AMAZON.HelpIntent': assistance,
            'AMAZON.FallbackIntent': fallback
            }
    # Gather the name of the intent sent from alexa
    intentName = event['request']['intent']['name'] 
    if intentName in intentFunc:
        return intentFunc[intentName](event)
    else:
        return stop(event) 


# Here we define the intent handler functions
def gpio_control(event):
    curtainCmds = ['open','close','shut']
    event['request']['intent']['slots']['status']['value']
    if curtainCmd in curtainCmds:
        confirmationMessage = 'You have chosen to {} the curtain'.format(curtainCmd)
        repromptMessage = 'Do you want to adjust the curtain setting again?'
        cardText = confirmationMessage
        cardTitle = confirmationMessage
        return output_json_builder_with_reprompt_and_card(confirmationMessage, cardText, cardTitle, repromptMessage, False)
    else:
        invalidCmd = 'The command you have supplied to the curtain is not supported'
        repromptMessage = 'Do you want to perform an action on the curtains?'
        cardText = 'Use a proper curtain command.'
        cardTitle = 'Invalid curtain command.'
        return output_json_builder_with_reprompt_and_card(invalidCmd, cardText, cardTitle, repromptMessage, False)
        
        
def stop(event):
    stop_MSG = "Thank you. Bye!"
    reprompt_MSG = ""
    card_TEXT = "Bye."
    card_TITLE = "Bye Bye."
    return output_json_builder_with_reprompt_and_card(stop_MSG, card_TEXT, card_TITLE, reprompt_MSG, True)
    
    
def assistance(event):
    #assistance_MSG = "You can choose among these players: " + ', '.join(map(str, Player_LIST)) + ". Be sure to use the full name when asking about the player."
    assistance_MSG = "This is the assistance message"
    reprompt_MSG = "Do you want to hear more about a pin"#particular player?"
    card_TEXT = "You've asked for help."
    card_TITLE = "Help"
    return output_json_builder_with_reprompt_and_card(assistance_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)

def fallback(event):
    fallback_MSG = "I can't help you with that, try rephrasing the question or ask for help by saying HELP."
    reprompt_MSG = "Do you want to hear more about a pin"#particular player?"
    card_TEXT = "You've asked a wrong question."
    card_TITLE = "Wrong question."
    return output_json_builder_with_reprompt_and_card(fallback_MSG, card_TEXT, card_TITLE, reprompt_MSG, False)


"""
    The response of our Lambda function should be in a json format. 
    That is why in this part of the code we define the functions which 
    will build the response in the requested format. These functions
    are used by both the intent handlers and the request handlers to 
    build the output.
"""

def plain_text_builder(text_body):
    text_dict = {}
    text_dict['type'] = 'PlainText'
    text_dict['text'] = text_body
    return text_dict

def reprompt_builder(repr_text):
    reprompt_dict = {}
    reprompt_dict['outputSpeech'] = plain_text_builder(repr_text)
    return reprompt_dict
    
def card_builder(c_text, c_title):
    card_dict = {}
    card_dict['type'] = "Simple"
    card_dict['title'] = c_title
    card_dict['content'] = c_text
    return card_dict    

def response_field_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title, reprompt_text, value):
    speech_dict = {}
    speech_dict['outputSpeech'] = plain_text_builder(outputSpeach_text)
    speech_dict['card'] = card_builder(card_text, card_title)
    speech_dict['reprompt'] = reprompt_builder(reprompt_text)
    speech_dict['shouldEndSession'] = value
    return speech_dict

def output_json_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title, reprompt_text, value):
    response_dict = {}
    response_dict['version'] = '1.0'
    response_dict['response'] = response_field_builder_with_reprompt_and_card(outputSpeach_text, card_text, card_title, reprompt_text, value)
    return response_dict


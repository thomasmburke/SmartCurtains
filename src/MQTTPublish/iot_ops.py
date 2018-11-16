import boto3
import logging
import json

# Initialize logger for CloudWatch logs
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class IoTOps:
    """
    Summary: Designed to check current status of thing by leveraging the
    thing's shadow. Using the input command and direction it will determine If
    it is a viable option and send a MQTT message to the thing

    Params: iotClient boto3 clientused to update thing's shadow and also send 
    messages to the thing
        topic STRING - the MQTT Topic to send a message to
        QoS - INT - Essentially the channel of a specifc topic to communicate
        over
    """
    def __init__(self, iotConfig):
        self.iotClient = boto3.client('iot-data', region_name='us-east-1')
        self.topic = iotConfig['topic']
        self.QoS = iotConfig['QoS']
        self.thingName = iotConfig['thingName']

    def check_thing_state(self, **payloadInputs):
        """
        Summary: Used to compare alexa command and thing's current state and 
        determine the proper payload to supply to the thing as well as building
        an Update for the thing's shadow

        Params: payload parameters supplied by the alexa slots

        Return: updated payload to be published to the thing
        """
        shadow = self.get_shadow()
        # gather action supplied by alexa command
        action = payloadInputs['status']
        # Generate dictionary to be published to mqtt topic
        mqttPayload = {}
        # Map Open to value 0 and close to value 1
        cutainEndValue = 0 if action == 'open' else 1
        # Get percent from alexa command
        commandPerc = payloadInputs['percentage']
        # Depending on direction get entire shadow or only the curtain specified
        curtainsToCheck = ['left', 'right'] if payloadInputs['direction'] == 'both' else [payloadInputs['direction']]
        # if a percentage is specified perform a calculation
        if commandPerc:
            # iterate through each of the curtains states
            for curtainToCheck in curtainsToCheck:
                # Get current percent from shadow
                currentThingPerc = shadow[curtainToCheck]
                # Check to see if they are trying to open a fully open curtain or close a fully closed curtain
                if currentThingPerc == curtainEndValue:
                    continue
                # See if percentage goes past limits based on payload status
                totalPerc = (currentThingPerc - commandPerc) if action == 'open' else (currentThingPerc + commandPerc)
                if totalPerc > 1 or totalPerc < 0:
                    # Percentage is past 100% or 0% so we must calculate the delta
                    deltaPerc = currentThingPerc if action == 'open' else (1 - currentThingPerc)
                    # Update Shadow to max/min value
                    shadow[curtainToCheck] = curtainEndValue
                else:
                    # if command is within limits proceed with that percentage
                    deltaPerc = commandPerc
                    # Update shadow with new delta added
                    shadow[curtainsToCheck] = totalPerc
                # Update mqttpayload for action to take place
                mqttPayload[curtainsToCheck] = {'action': action, 'percentage': deltaPerc}
        # If no percentage is specified it defaults to a full open or close
        else:
            for curtainToCheck in curtainsToCheck:
                # Get current percent from shadow
                currentThingPerc = shadow[curtainToCheck]
                # Check to see if they are trying to open a fully open curtain or close a fully closed curtain
                if currentThingPerc == curtainEndValue:
                    continue
                deltaPerc = currentThingPerc if action == 'open' else (1 - currentThingPerc)
                # Update Shadow to max/min value
                shadow[curtainToCheck] = curtainEndValue
                # Update mqttpayload for action to take place
                mqttPayload[curtainsToCheck] = {'action': action, 'percentage': deltaPerc}
        if mqttPayload:
            self.publish_mqtt_message(payload=mqttPayload)
            self.update_shadow(payload=shadow['state'])
        return mqttPayload

    def publish_mqtt_message(self, payload):
        """                                                                        
        Description: Send MQTT message to MQTT Topic                         
                                                                                   
        Return: None                                                          
        """                                                                       
        # Publish a MQTT message to a topic for our thing to ingest               
        logger.info('publishing MQTT message to topic: {}'.format(self.topic))         
        self.iotClient.publish(                                                           
            topic=self.topic,                     
            qos=self.QoS,                                                               
            payload=json.dumps(payload)                                   
        )  
        return

    def update_shadow(self, payload):
        """
        Summary: Updates a things shadow for a specified thing

        Return The state information in a JSON format
        """
        response = self.iotClient.update_thing_shadow(
            thingName=self.thingName,
            payload=json.dumps(payload)
        )
        return response

    def get_shadow(self):
        """
        Summary: gets thing shadow for a specified thing

        Return: The state information in JSON format
        """
        response = self.iotClient.get_thing_shadow(
            thingName=self.thingName
        )
        return response

    def delete_shadow(self):
        """
        Summary: deletes thing shadow for a specified thing

        Return: The state information in a JSON format
        """
        response = self.iotClient.delete_thing_shadow(
            thingName=self.thingName
        )
        return response

# TODO:
# Need a Subscription to the reject shadow topic in case of failure
# $aws/things/pi/shadow/update/rejected

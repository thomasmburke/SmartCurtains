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

    def mqtt_message(self, curtainCmd, curtainDirection):
        """                                                                        
        Description: Send MQTT message to raspberry pi                             
                                                                                   
        Return: TBD                                                                
        """                                                                        
        # Publish a MQTT message to a topic for our thing to ingest                
        logger.info('publishing MQTT message to topic: {}'.format(self.topic))          
        self.iotClient.publish(                                                            
            topic=self.topic,  # '$aws/things/pi/shadow/update',                        
            qos=self.QoS,                                                               
            payload=json.dumps({'command': curtainCmd,                             
                'direction': curtainDirection})                                    
        )   

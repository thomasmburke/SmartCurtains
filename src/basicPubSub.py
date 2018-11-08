# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import os
import json

class MQTTPoller:

    def __init__(self):
        #################################
        #                               #
        #     GET ALL ENV VARIABLES     #
        #                               #
        #################################
        self.rootCA = os.environ['ROOT_CA']
        self.privKey = os.environ['IOT_PRIVATE_KEY']
        self.iotCert = os.environ['IOT_CERTIFICATE']
        self.iotEndpoint = os.environ['IOT_ENDPOINT']
        self.MQTT_PORT = 8883

    def poll_mqtt_messages(self):
        """
        Summary: Polls a specific MQTT topic for messages and performs the 
        operation requested.

        Return: TBD
        """

        #################################
        #                               #
        #     CONFIGURE CONNECTION      #
        #                               #
        #################################
        # For certificate based connection
        myMQTTClient = AWSIoTMQTTClient("raspberrypi")
        # Configurations
        # For TLS mutual authentication
        myMQTTClient.configureEndpoint(hostName=self.iotEndpoint, portNumber=self.MQTT_PORT)
        myMQTTClient.configureCredentials(CAFilePath=self.rootCA, KeyPath=self.privKey, CertificatePath=self.iotCert)
        myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

        #################################
        #                               #
        #     ESTABLISH CONNECTION      #
        #                               #
        #################################
        myMQTTClient.connect()
        # Subscribe to topic that the alexa lambda function is publishing to
        myMQTTClient.subscribe(topic="raspberrypi3", QoS=0, callback=self.customCallback)
        while True:
            pass


    # Custom MQTT message callback
    def customCallback(self,client, userdata, message):
        print("Received a new message: ")
        print(message.payload)
        print("from topic: ")
        print(message.topic)
        print("--------------\n\n")
        if message.payload == 'open':
            print('received message and ready for action')


if __name__ == '__main__':
    MQTTPoller().poll_mqtt_messages()

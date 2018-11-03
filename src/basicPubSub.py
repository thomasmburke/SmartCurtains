# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
import os
import json


def poll_mqtt_messages():
    """
    Summary: Polls a specific MQTT topic for messages and performs the 
    operation requested.

    Return: TBD
    """
    #################################
    #                               #
    #     GET ALL ENV VARIABLES     #
    #                               #
    #################################
    rootCA = os.environ['ROOT_CA']
    privKey = os.environ['IOT_PRIVATE_KEY']
    iotCert = os.environ['IOT_CERTIFICATE']
    iotEndpoint = os.environ['IOT_ENDPOINT']
    MQTT_PORT = 8883


    #################################
    #                               #
    #     ESTABLISH CONNECTION      #
    #                               #
    #################################
    # For certificate based connection
    myMQTTClient = AWSIoTMQTTClient("raspberrypi")
    # Configurations
    # For TLS mutual authentication
    myMQTTClient.configureEndpoint(hostName=iotEndpoint, portNumber=MQTT_PORT)
    myMQTTClient.configureCredentials(CAFilePath=rootCA, KeyPath=privKey, CertificatePath=iotCert)
    myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    payload = {
            'status': 'available'
            }


    myMQTTClient.connect()
    myMQTTClient.publish(topic="raspberrypi3", payload=json.dumps(payload),QoS=0)
    myMQTTClient.subscribe(topic="raspberrypi3", QoS=0, callback=customCallback)
    while True:
        myMQTTClient.publish(topic="raspberrypi3", payload=json.dumps(payload),QoS=0)
        sleep(60)
    #myMQTTClient.unsubscribe(topic="myTopic")
    myMQTTClient.disconnect()


# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

if __name__=='__main__':
    poll_mqtt_messages()

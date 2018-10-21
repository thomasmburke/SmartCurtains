# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from time import sleep
import os
import json

#Gather paths for MQTT client from environment
rootCA = os.environ['ROOT_CA']
privKey = os.environ['IOT_PRIVATE_KEY']
iotCert = os.environ['IOT_CERTIFICATE']
iotEndpoint = os.environ['IOT_ENDPOINT']
MQTT_PORT = 8883

# For certificate based connection
myMQTTClient = AWSIoTMQTTClient("raspberrypi")
# Configurations
# For TLS mutual authentication
myMQTTClient.configureEndpoint(hostName=iotEndpoint, portNumber=MQTT_PORT)
myMQTTClient.configureCredentials(CAFilePath=rootCA, KeyPath=privKey, CertificatePath=iotCert)
# For Websocket, we only need to configure the root CA
# myMQTTClient.configureCredentials("YOUR/ROOT/CA/PATH")
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

payload = {
        'status': 'available'
        }


myMQTTClient.connect()
myMQTTClient.publish(topic="raspberrypi", payload=json.dumps(payload),QoS=0)
myMQTTClient.subscribe(topic="tom", QoS=0, callback=customCallback)
myMQTTClient.publish(topic="raspberrypi", payload=json.dumps(payload),QoS=0)
#myMQTTClient.unsubscribe(topic="myTopic")
myMQTTClient.disconnect()

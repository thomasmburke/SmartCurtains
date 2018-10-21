import json
import boto3

def lambda_handler(event, context):
    client = boto3.client('iot-data', region_name='us-east-1')
    response = client.publish(
        topic='raspberrypi3',#'$aws/things/pi/shadow/update',
        qos=1,
        payload=json.dumps({"foo":"bar"})
    )
    return {
        "statusCode": 200,
        "body": json.dumps('Hello from Lambda!')
    }

import os
import boto3
import logging
from botocore.exceptions import ClientError
import json
from twilio.rest import Client

# Get parameters from environment variables
twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']
sender_number = os.environ['SENDER_NUMBER']
receiver_number = os.environ['RECEIVER_NUMBER']

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_secret(secret_name):
    region_name = "us-east-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        logger.error(e)
        raise e
    else:
        # Decrypts secret using the associated KMS CMK
        # Depending on whether the secret is a string or binary, one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            return get_secret_value_response['SecretString']
        else:
            logger.error("Secret binary not supported.")
            raise NotImplementedError("Secret binary not supported.")

def send_sms(body):
    account_sid = json.loads(get_secret(twilio_account_sid))
    auth_token = json.loads(get_secret(twilio_auth_token))
    client = Client(account_sid['twilio-account-sid'], auth_token['twilio-auth-token'])
    try:
        sender=json.loads(get_secret(sender_number))
        receiver=json.loads(get_secret(receiver_number))
        logger.info(f"receiver:{receiver}")
        message = client.messages.create(
            body=body,
            from_=sender['sender-number'],
            to=receiver['receiver-number']
            )
    except Exception as e:
        logger.error(e)
        raise e

def lambda_handler(event, context):
    # print(event)
    message = event['message']
    send_sms(message)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

import os
import boto3
import logging
from botocore.exceptions import ClientError
import json
import pytz
import datetime

# Initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Instantiate User List
USERS = {
    "UJ9DBQFHV": "JP Pollak",
    "U013TLTLVK8": "Phil",
    "U017DSCSBDG": "Jeff Chambers",
    "U01D88HF1QW": "Tiphany Jones",
    "U01E4FEGNA2": "Ben Tseytlin",
    "U01FPDV27J7": "Kerry Keys",
    "U01N27PGYF7": "Barbara Tannenbaum",
    "U01RLCHHY87": "Eddie Cruz",
    "U02DYUZQ13M": "Yuri Fukuda",
    "U02JUT1A5UZ": "Zhenya Lindgardt",
    "U041M7X3EBZ": "Matt Stack",
    "U04BN660VGR": "Naomi Cosman",
    "U04LL73HPL4": "Abdool Bhollah",
    "U058QQKH3AL": "Sharon Zink",
    "U06ULB8DBMZ": "Simon",
    "U03566PK5EY": "Richard Gakuba",
    "U0295UUV43D": "Jeff Kenney",
    "U03EEQ1NSJW": "Patrick Carter"
}

CHANNELS = {
    "G01HX869U3T": "not-just-apple-health",
    "C01DJNGA6HK": "aws-alerts",
    "C0295KX3ZHD": "aws-root",
    "C02H078K7EV": "commonhealth-alerts",
    "CQNHFRQUX": "engineering",
    "CG3977JG5": "general",
    "C0235QSF9L6": "mobot-tcp"
}

def check_channel(channel_id):
    if channel_id in CHANNELS:
        return CHANNELS[channel_id]
    else:
        return "Direct Message"

def check_user(user_id):
    if user_id in USERS:
        return USERS[user_id]
    else:
        return "User ID not found."

def is_between_time_range(dt, start_hour=8, start_minute=0, end_hour=10, end_minute=30, tz='US/Eastern'):
    """
    Checks if a given datetime object is between the specified start and end times in the given time zone.
    Returns:
        bool: True if the datetime object is within the specified time range, False otherwise.
    """
    est = pytz.timezone(tz)
    start_time = est.localize(datetime.datetime.combine(dt.date(), datetime.time(start_hour, start_minute)))
    end_time = est.localize(datetime.datetime.combine(dt.date(), datetime.time(end_hour, end_minute)))


    dt_with_tz = est.localize(dt)

    return start_time <= dt_with_tz < end_time


def lambda_handler(event, context):
    # print(event)
    if 'body' in event:
        body = json.loads(event['body'])
        if body['type'] == 'url_verification':
            challenge = body['challenge']
            return {
               'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/plain'
                },
                'body': challenge
            }
        else:
            user = check_user(body['event']['user'])
            message = f"Slack Message from {user}: message: {body['event']['text']}"
            if body['event']['channel']:
                channel = check_channel(body['event']['channel'])
                message = f"Slack Message from {user} in {channel}: message: {body['event']['text']}"
            eastern_tz=pytz.timezone('US/Eastern')
            timestamp = datetime.datetime.now(eastern_tz)
            if is_between_time_range(timestamp.replace(tzinfo=None))==True:
                payload = {
                'message': message,
                }
                lambda_client = boto3.client('lambda')
                lambda_client.invoke(
                    FunctionName='arn:aws:lambda:us-east-1:283079628040:function:send-text',
                    InvocationType='Event',
                    Payload=json.dumps(payload)
                )
            else:
                logger.info(f"Slack Message not sent. Current time is {timestamp}")
            
            return {
                'statusCode': 200,
                'body': 'Hello from Lambda'
            }
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# "Josep Valls-Vargas" <josep@valls.name>
#

import json

try:
    import boto3
except:
    boto3 = None
    pass

TABLE_NAME = 'logger_v1'

def lambda_handler(event, context):
    log_event(event)
    body = AlexaResponse("Hello","This is an Alexa response.").toAlexa()
    return {'statusCode':200,'headers':{'Content-Type': 'application/json'},'body':json.dumps(body)}

import decimal
def replace_decimals(obj):
    if isinstance(obj, list):
        for i in xrange(len(obj)):
            obj[i] = replace_decimals(obj[i])
        return obj
    elif isinstance(obj, dict):
        for k in obj.iterkeys():
            obj[k] = replace_decimals(obj[k])
        return obj
    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj

def log_event(event, log_key='log', last_key='last'):
    if last_key:
        persist_document(last_key, event)
    log = load_document(log_key) or {}
    if 'req_history' not in log or not log['req_history']: log['req_history'] = []
    log['req_history'].append(event)
    persist_document(log_key,log)

def check_table():
    dynamodb = boto3.resource('dynamodb')
    try:
        table = dynamodb.Table(TABLE_NAME)
        table.creation_date_time
    except:
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[
                {
                    'AttributeName': 'key',
                    'KeyType': 'HASH'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'key',
                    'AttributeType': 'S'
                },

            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        table = dynamodb.Table(TABLE_NAME)
    return table

def load_document(key):
    if boto3 is not None:
        try:
            table = check_table()
            response = table.get_item(
                Key={
                    'key': key,
                }
            )
            if 'Item' in response:
                document = replace_decimals(response['Item']['document'])
            else:
                document = {}
            return document
        except Exception as e:
            print "Exception",e
    return None

def persist_document(key, document):
    if boto3 is not None:
        if not key:
            key = 'empty'

        dynamodb = boto3.resource('dynamodb')
        table = check_table()
        table.put_item(
            Item={'key': key, 'document': document}
        )
        return True
    else:
        return False

class AlexaResponse(object):
    def __init__(self, title, response, reprompt=None, model=None, ssml=None, card=None):
        self.title = title
        self.response = response
        self.reprompt = reprompt
        self.model = model
        self.ssml = ssml
        self.card = card
    def __str__(self):
        return "%s: %s" % (self.title, self.response)
    def toAlexa(self):
        return {
            "version": "1.0",
            "sessionAttributes": {'model': (self.model.serialize() if self.model else {})},
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": self.response
                },
                "card": {
                    "type": "Simple",
                    "title": self.title,
                    "content": self.response if not self.card else self.card
                },
                "reprompt": {
                    "outputSpeech": {
                        "type": "PlainText",
                        "text": (self.reprompt or self.response)
                    }
                },
                "shouldEndSession": ((not self.model.running) if self.model else True)
            }
        }
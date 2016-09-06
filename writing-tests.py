#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# "Josep Valls-Vargas" <josep@valls.name>
#

from YOUR_SKILL_FILE import *
import unittest

class TestLambda(unittest.TestCase):
    def test_new_complete_game(self):
        req = testing_encode_intent("NewIntent",testing_encode_slots('alpha'),{})
        resp = lambda_handler(req,{})
        self.printResp(resp)
        self.assertNotInResp('letter a',resp)
        self.assertInResp('welcome', resp)
        self.assertNotInResp('don\'t know', resp)
        req = testing_encode_intent_from_resp("GuessIntent",testing_encode_slots('alpha'),resp)
        resp = lambda_handler(req, {})
        self.printResp(resp)
        self.assertInResp('letter a', resp)
        self.assertNotInResp('welcome', resp)
        self.assertNotInResp('don\'t know', resp)
        req = testing_encode_intent_from_resp("GuessIntent",{},resp)
        resp = lambda_handler(req, {})
        self.printResp(resp)
        self.assertInResp('didn\'t', resp)
        resp = lambda_handler(testing_encode_intent_from_resp("GuessIntent",testing_encode_slots('papa'),resp), {})
        self.printResp(resp)
        self.assertInResp('not',resp)
        resp = lambda_handler(testing_encode_intent_from_resp("GuessIntent", testing_encode_slots('a'), resp), {})
        self.printResp(resp)
        self.assertInResp('already', resp)
        resp = lambda_handler(testing_encode_intent_from_resp("GuessIntent", testing_encode_slots('m'), resp), {})
        self.printResp(resp)
        resp = lambda_handler(testing_encode_intent_from_resp("GuessIntent", testing_encode_slots('z'), resp), {})
        self.printResp(resp)
        resp = lambda_handler(testing_encode_intent_from_resp("GuessIntent", testing_encode_slots('n'), resp), {})
        self.printResp(resp)
        resp = lambda_handler(testing_encode_intent_from_resp("GuessIntent", testing_encode_slots('o'), resp), {})
        self.printResp(resp)
        resp = lambda_handler(testing_encode_intent_from_resp("ShootIntent", testing_encode_slots('c'), resp), {})
        self.printResp(resp)
        resp = lambda_handler(testing_encode_intent_from_resp("AMAZON.HelpIntent", {}, resp), {})
        self.printResp(resp)
        resp = lambda_handler(testing_encode_intent_from_resp("GuessIntent", testing_encode_slots('zulu'), resp), {})
        self.printResp(resp)
        resp = lambda_handler(testing_encode_intent_from_resp("AMAZON.HelpIntent", {}, resp), {})
        self.printResp(resp)
        resp = lambda_handler(testing_encode_intent_from_resp("GuessIntent", testing_encode_slots('alpha'), resp), {})
        self.printResp(resp)
        resp = lambda_handler(testing_encode_intent_from_resp("AMAZON.HelpIntent", {}, resp), {})
        self.printResp(resp)

    def assertInResp(self,text,resp):
        return resp and self.assertIn(text,resp['response']['outputSpeech']['text'].lower())
    def assertNotInResp(self,text,resp):
        return resp and self.assertNotIn(text,resp['response']['outputSpeech']['text'].lower())
    def printResp(self,resp):
        if resp:
            print resp['response']['outputSpeech']['text']
        else:
            "NONE"

def testing_encode_slots(letter):
    return {'Letter': {'value': letter}}
def testing_encode_intent_from_resp(intent,slots,resp):
    session_attributes = resp['sessionAttributes'] if resp and 'sessionAttributes' in resp else {}
    return testing_encode_intent(intent, slots, session_attributes)
def testing_encode_intent(intent,slots,session_attributes):
    return {
        "session": {
            "sessionId": "SessionId.4d96f5de-f93d-4132-9232-XXXXXXXXXXXX",
            "application": { "applicationId": "amzn1.ask.skill.3e7ce8c3-fe25-4b28-b1e7-XXXXXXXXXXXX"},
            "attributes": session_attributes,
            "user": { "userId": "amzn1.ask.account.XXXXXXXXXXXX"},
            "new": True
        },
        "request": {
            "type": "IntentRequest",
            "requestId": "EdwRequestId.8e040071-5bd0-42f5-be98-XXXXXXXXXXXX",
            "locale": "en-US",
            "timestamp": "2016-08-03T01:22:35Z",
            "intent": {
                "name": intent,
                "slots": slots
            }
        },
        "version": "1.0"
    }


def event1():
    return {
  "session": {
    "sessionId": "SessionId.ce10fbab-18a3-4403-8ad8-XXXXXXXXXXXX",
    "application": {
      "applicationId": "amzn1.ask.skill.18a84c1b-a040-4d8e-8586-XXXXXXXXXXXX"
    },
    "attributes": {},
    "user": {
      "userId": "amzn1.ask.account.XXXXXXXXXXXX"
    },
    "new": True
  },
  "request": {
    "type": "IntentRequest",
    "requestId": "EdwRequestId.1b12d832-9003-403a-8f17-XXXXXXXXXXXX",
    "locale": "en-US",
    "timestamp": "2016-08-25T01:31:29Z",
    "intent": {
      "name": "GuessIntent",
      "slots": {
        "Letter": {
          "name": "Letter",
          "value": "x"
        }
      }
    }
  },
  "version": "1.0"
}

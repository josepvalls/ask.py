#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# "Josep Valls-Vargas" <josep@valls.name>
#

import random, operator, copy


try:
    import boto3
except:
    boto3 = None
    pass

TABLE_NAME = 'A_TABLE_IN_DYNAMO_DB' #TODO replace with your table name
ALWAYS_PERSIST = True
ENVIRONMENT_MODELS = {}
RELOAD_ENVIRONMENT_MODELS = True
ALLOWED_APPLICATIONS = [
    'amzn1.echo-sdk-ams.app.[unique-value-here]',
    'amzn1.ask.skill.dad8a77a-a627-45a8-ae01-XXX',
    'YOUR_SKILL_ID', # TODO replace with your skill ID
    'YOUR_TESTING_SKILL_ID' # if you need an additional one for testing
]

def lambda_handler(event, context):
    log_event(event)
    if not event or 'version' not in event or 'session' not in event or 'user' not in event['session']:
        return {"error": "bad trigger"}
    else:
        application_id = event['session']['application']['applicationId']
        if application_id not in ALLOWED_APPLICATIONS:
            return
        client_id = event['session']['user']['userId']
        if 'session' in event and 'attributes' in event['session'] and 'model' in event['session']['attributes']:
            # try loading the current model form the session
            model_data = event['session']['attributes']['model']
        else:
            # try loading from persisted data
            document = load_document(client_id)
            model_data = document['model'] if document and 'model' in document else {}
            event_history = document['event_history'] if document and 'event_history' in document else []
        model = unserialize(model_data)
        if not model:
            model = MYMODEL(client_id,None)
        if True:
            if event['request']['type'] == 'IntentRequest':
                key = event['request']['type'] + '.' + event['request']['intent']['name']
                args = event['request']['intent']['slots'] if 'slots' in event['request']['intent'] else {}
            else:
                key = event['request']['type']
                args = {}
            action = model.get_service_translation_layer('alexa').get(key,'do_unknown_command')
            resp = model.do(action,args,key)
        if resp and resp.model and not resp.model.running or ALWAYS_PERSIST and resp and resp.model:
            document = {}
            document['model'] = resp.model.serialize()
            persist_document(client_id,document)
        if resp and not key == 'SessionEndedRequest':
            log_event(resp.toAlexa())
            return resp.toAlexa()
        else:
            return None
            # https://forums.developer.amazon.com/questions/32359/can-we-emit-a-good-bye-message-in-sessionendedrequ.html
            # "Your service cannot send back a response to a SessionEndedRequest." The SessionEndedRequest is called when Alexa times out by the web service after which point it no longer accepts responses. As a result it is not possible to provide a goodbye message.

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

def log_event(event):
    return None
    log = load_document('log')
    if log:
        if 'req_history' not in log or not log['req_history']: log['req_history'] = []
        log['req_history'].append(event)
        persist_document('log',log)

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
        table = dynamodb.Table(TABLE_NAME)
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


def unserialize(data):
    if 'client_id' not in data or 'model_name' not in data:
        return None
    global ENVIRONMENT_MODELS
    if not ENVIRONMENT_MODELS:
        def all_subclasses(cls):
            return cls.__subclasses__() + \
                   [g for s in cls.__subclasses__() for g in all_subclasses(s)]

        ENVIRONMENT_MODELS = dict([(i.model_name, i) for i in all_subclasses(BaseModel)])
    return ENVIRONMENT_MODELS[data['model_name']].unserialize(data)

class BaseModel(object):
    model_name = 'BaseModel'
    model_title = "Base Model"
    model_description = "Internal, do not use"
    STATE_DEFAULT = 'bm0'
    TRANSITION_STATE_ANY = '*'  # wildcard used for catching any transitions
    TRANSITION_ACTION_ANY = '*' # wildcard used for catching any transitions
    TRANSITION_ACTION_PASSTHROUGH = '*' # perform the requested action as is
    TRANSITION_OUTPUT_SAME = '=' # revert state after action regardless of change
    TRANSITION_OUTPUT_BY_ACTION = '*' # let the function change the state
    # this is a list of lists, for each item:
    #   input_state|*, input_action|*, action|*, next_state|*
    # by default, [*,*,*,*] means that regardless of the state, execute the requested function and let the function change the state
    # by default, [*,X,Y,Z] means that regardless of the state, when receiving a call to X, execute Y instead and afterwards set the state to Z
    model_fst = []
    def __init__(self, client_id, previous_model):
        self.client_id = 'None'
        self.running = True
        self.stats = {'started':0,'completed':0}
        self.state = self.get_default_state()
        self._last_reprompt = None
    def get_default_state(self):
        return BaseModel.STATE_DEFAULT
    def get_default_rule(self):
        return [BaseModel.TRANSITION_STATE_ANY,BaseModel.TRANSITION_ACTION_ANY,BaseModel.TRANSITION_ACTION_PASSTHROUGH,BaseModel.TRANSITION_OUTPUT_BY_ACTION]
    def get_fst(self):
        return []
    def do(self, command_name, args, intent_key):
        for rule in self.get_fst():
            if (rule[0]==self.state or rule[0]==self.TRANSITION_STATE_ANY) and \
                    (rule[1]==command_name or rule[1]==self.TRANSITION_ACTION_ANY):
                break
        else:
            rule = self.get_default_rule()
        if not rule[2]==self.TRANSITION_ACTION_PASSTHROUGH:
            command_name = rule[2]
        state_ = self.state

        args['intent_key'] = intent_key
        args['state'] = self.state
        args['command_name'] = command_name

        func = getattr(self,command_name)
        resp = func(args)

        if rule[3]==self.TRANSITION_OUTPUT_SAME:
            self.state = state_
        elif not rule[3]==self.TRANSITION_OUTPUT_BY_ACTION:
            self.state = rule[3]
        return resp
    def serialize(self):
        ret = {}
        ret['model_name'] = self.model_name
        ret['client_id'] = self.client_id
        ret['stats'] = self.stats
        ret['state'] = self.state
        return ret
    @classmethod
    def unserialize(cls, data):
        ret = cls(data['client_id'])
        cls.post_load(ret,data)
    @classmethod
    def post_load(cls,self,data):
        if 'stats' in data:
            self.stats = data['stats']
        if 'state' in data:
            self.state = data['state']
    def __str__(self):
        return self.__class__.__name__ + ' ('+self.client_id+'): ' + str(self.environment)
    def start_session(self):
        self.stats['started'] = self.stats.get('started',0)+1
    def finish_session(self):
        self.stats['completed'] = self.stats.get('completed', 0) + 1
        self.running = False
    def do_new(self):
        self.start_session()
        return self.response("Welcome","Welcome")
    def do_quit(self):
        self.finish_session()
        return self.response("Good bye",self.text_quit())
    def last_reprompt(self):
        if self._last_reprompt:
            return " " + self._last_reprompt
        else:
            return ""
    def do_unknown_command(self):
        return self.response("I'm not sure what you want me to do.", "Sorry, I'm not sure what you want me to do right now." + self.last_reprompt())
    def do_echo(self, slots = None):
        return AlexaResponse("Echo",str(slots) if slots else "slots is None")
    def response(self,  title, response, reprompt=None, ssml=None, card=None):
        self._last_reprompt = reprompt or response
        return AlexaResponse(title, response, reprompt=reprompt, model=self, ssml=ssml, card=card)
    def text_quit(self):
        return "Thanks for playing!"

class MYMODEL(BaseModel):
    model_name = "Hangman"
    model_title = "Audio Hangman"
    model_description = "Audio Hangman, train your brain!"

    def get_fst(self):
        return []
    def get_default_state(self):
        return 'nothing'
    def get_default_rule(self):
        return ['*', '*', 'do_echo', '=']
    def get_service_translation_layer(self,service):
        if service == 'alexa':
            return {
                'LaunchRequest': 'do_resume',
                'IntentRequest.NewIntent': 'do_new',
                'IntentRequest.GuessIntent': 'do_guess',
                'IntentRequest.AMAZON.StartOverIntent': 'do_new',
                'IntentRequest.AMAZON.StopIntent': 'do_cancel',
                'IntentRequest.AMAZON.CancelIntent': 'do_cancel',
                'IntentRequest.AMAZON.HelpIntent': 'do_help',
                'IntentRequest.AMAZON.YesIntent': 'do_yes',
                'IntentRequest.AMAZON.NoIntent': 'do_no',
                'SessionEndedRequest': 'do_quit',
            }

    def serialize(self):
        ret = BaseModel.serialize(self)
        ret.update({'word': self.word})
        ret.update({'tries': self.tries})
        ret.update({'guesses': self.guesses})
        ret.update({'max_errors': self.max_errors})
        return ret
    @classmethod
    def unserialize(cls, data):
        self = cls(data['client_id'],None)
        MYMODEL.post_load(self, data)
        return self
    @classmethod
    def post_load(cls,self,data):
        BaseModel.post_load(self, data)
        self.word = data.get('word','amazon')
        self.tries = data.get('tries',[])
        self.guesses = data.get('guesses',[])
        self.max_errors = data.get('max_errors',99)
    def get_word(self):
        # TODO compute player skill and get a word based on their skill
        words = 'time,like,know,good,down,never,shall,come,make,work,life'.split(',')
        return random.choice(words)
    def do_new(self):
        self.start_session()
        self.word = self.get_word()
        self.tries = []
        self.guesses = []
        self.max_errors = 13
        title = "Welcome to a new game of Audio Hangman"
        response = title + '. I thought about a %d letter word. Can you try guessing it\'s letters?' % len(self.word)
        self.state = 'playing'
        return self.response(title,response)
    def do_guess(self, slots=None):
        if not slots or 'Letter' not in slots:
            return self.do_bad_guess()
        letter = slots['Letter']['value'][0].lower()
        penalty = False
        if letter not in self.tries:
            self.tries.append(letter)
            if letter in self.word:
                self.guesses.append(letter)
                s_ok,s_miss = self.get_stats()
                if len(s_ok)==len(self.word):
                    self.state = 'endgame'
                    self.finish_session()
                    resp = "Congratulations! You guessed all the letters of the word; it was: %s." % self.word
                    resp += ' ' + self.text_hint()
                    return self.response("Congratulations!", resp)
                else:
                    out = "The letter %s is in the word at the %s." % (letter.upper(),self.text_positions_letter(letter))
            else:
                penalty = True
                out = "The letter %s is not in the word." % letter.upper()
        else:
            penalty = True
            out = "You already guessed %s.;" % letter.upper()
            out += " Say help at any time to check your current status."

        if penalty:
            self.max_errors -= 1
            if self.max_errors > 0 and self.max_errors % 3 == 0 or self.max_errors==1:
                out += " " + self.text_lives()
        if self.max_errors <= 0:
            self.state = 'endgame'
            self.finish_session()
            return self.response("Failed", "You got hung. "+self.text_status_short()+" but you did not guess the word; it was: "+self.word)
        else:
            return self.response("Guess", out + ' Continue.')
    def get_stats(self):
        ok = []
        miss = []
        for i in enumerate(self.word):
            if i[1] in self.guesses:
                ok.append(i)
            else:
                miss.append(i)
        return ok,miss
    def do_bad_guess(self):
        response = "I didn't get your guess, try again."
        return self.response("Bad guess",response,response)
    def do_resume_long(self):
        title = "Welcome back"
        response = "Welcome back to your game. " + self.text_status_long()
        return self.response(title, response)
    def do_resume_short(self):
        title = "Welcome back"
        response = "Welcome back, " + self.text_status_short()
        return self.response(title, response)
    def do_help(self, args = None):
        resp = self.text_help()
        return self.response("Help",resp + " Check your Alexa app for more information.", card = resp + " " + self.phonetic_list())
    def do_confirm_quit(self):
        return self.response("Quitting?","Are you sure you want to quit?")
    def do_confirm_new(self):
        return self.response("New game?","Are you sure you want to start a new game?")
    def phonetic_list(self):
        return "This is a list with the phonetic words you can use:\nAdams Alpha\nBeta Boston Bravo\nCharlie Chicago\nDelta Denver\nEasy Echo Epsilon\nFoxtrot Frank\nGamma George Golf\nHenry Hotel\nIda India Iota\nJohn Juliet\nKappa Kilo King\nLambda Lima Lincoln\nMary Mike Mu\nNew York\nNovember\nOcean Omega Oscar\nPapa Peter Pi\nQuebec Queen\nRho Roger Romeo\nSierra Sigma Sugar\nTango Tau Thomas\nUniform Union Upsilon\nVictor\nWhiskey William\nXray\nYankee Young\nZero Zeta Zulu"
    def text_lives(self):
        if self.max_errors > 1:
            return "You have %d lives remaining." % self.max_errors
        elif self.max_errors == 1:
            return "You have one life remaining."
    def text_positions_letter(self,letter):
        positions = []
        for i,j in enumerate(self.word):
            if letter==j:
                positions.append(i)
        return self.text_positions(positions)
    def text_positions(self,lst):
        return self.text_list([self.text_ordinal(i+1) for i in lst])+' '+('position' if len(lst)==1 else 'positions')
    def text_ordinal(self, num):
        return {1:'first',2:'second',3:'third',4:'fourth',5:'fifth',6:'sixth',7:'seventh',8:'eighth',9:'ninth',10:'tenth',11:'eleventh',12:'twelfth'}[num]
    def text_list(self,lst, last='and'):
        if len(lst)==1:
            return lst[0]
        else:
            return ', '.join(lst[0:-1]) + ' ' + last + ' ' + lst[-1]
    def text_status_short(self):
        s_ok,s_miss = self.get_stats()
        return "You guessed %d out of %d letters" % (len(s_ok),len(self.word))
    def text_status_long(self):
        s_ok,s_miss = self.get_stats()
        out = "The word I thought about has %s letters." % len(self.word)
        if not s_ok:
            out += " You have not guessed any letter yet."
        else:
            lst = ["the letter %s in the %s" % (i[1].upper(),self.text_ordinal(i[0]+1)) for i in s_ok]
            out += " You have guessed: " + self.text_list(lst) + (" position." if len(s_ok)==1 else " positions.")
            out += " You are missing "+("%d letters" % len(s_miss) if len(s_miss)>1 else "a letter")+" in the " + self.text_positions([i[0] for i in s_miss])
        out += ". " + self.text_lives()
        failed = set(self.tries) - set([i[1] for i in s_ok])
        if failed:
            out += " You tried the following letters not in the word: " + self.text_list(["%s." % i.upper() for i in sorted(failed)])
        return out
    def text_help(self):
        return self.text_status_long() + " " + self.text_instructions()
    def text_instructions(self):
        return "You can say: Guess W, check Whiskey or just William."
    def text_quit(self):
        return "Thanks for playing!"
    def text_hint(self):
        return "If you want to play again, say: Alexa, start Audio Hangman."


if not RELOAD_ENVIRONMENT_MODELS:
    ENVIRONMENT_MODELS['Hangman'] = MYMODEL

test_event = {
  "session": {
    "new": False,
    "sessionId": "session1234",
    "attributes": {},
    "user": {
      "userId": None
    },
    "application": {
      "applicationId": "amzn1.echo-sdk-ams.app.[unique-value-here]"
    }
  },
  "version": "1.0",
  "request": {
    "intent": {
      "slots": {
        "Color": {
          "name": "Color",
          "value": "blue"
        }
      },
      "name": "MyColorIsIntent"
    },
    "type": "IntentRequest",
    "requestId": "request5678"
  }
}

test_event = {
  "session": {
    "sessionId": "SessionId.976806f0-337e-44f4-ac7a-XXX",
    "application": {
      "applicationId": "amzn1.ask.skill.dad8a77a-a627-45a8-ae01-XXX"
    },
    "attributes": {},
    "user": {
      "userId": "amzn1.ask.account.XXX"
    },
    "new": True
  },
  "request": {
    "type": "IntentRequest",
    "requestId": "EdwRequestId.6be82751-32f8-4754-9365-XXX",
    "locale": "en-US",
    "timestamp": "2016-09-27T23:42:44Z",
    "intent": {
      "name": "GetLocalGeneralIntent",
      "slots": {
        "Country": {
          "name": "Country"
        },
        "City": {
          "name": "City",
          "value": "Barcelona"
        }
      }
    }
  },
  "version": "1.0"
}

lambda_handler(test_event,{})
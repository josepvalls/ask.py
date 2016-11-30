# ask.py
Single file template, examples and utilities for creating Amazon Alexa's skills (ASK) using Python

## Why?
Amazon provides pretty cool tutorials and examples but most of them are written in Node.js. I thought I'd share my findings with other developers who may prefer Python instead.

## How to get started?
* In line 44, replace MYMODEL for your model class name. Tip: if you have a separate class for the tutorial, you can create and instance of your tutorial class.
* Implement your skill by inheriting from BaseModel. See MYMODEL for an example. Tip: try to keep the text in separate functions/templates so you can reuse it or override in subclasses; I use this approach for the tutorial.
* Start by defining the translation layer and finite state machine, see the examples provided in MYMODEL for get_service_translation_layer() and get_fst().

## How to get it up and running?
This is intended to work on AWS infrastructure. It uses ASK, Lambda and DynamoDB.
* Setup your skill, when it comes to configuring the endpoint, go to Lambda.
* Create a new lambda using the Python Alexa template. Select *edit code inline* and copy/paste the code from your single-file-template.py file.
* Copy the ARN to the skill.
* Create your Dynamodb table.


## What else is included?
* A little utility to generate utterances given a grammar (with an example of my Audio Hangman and Audio Battleship skills).
* An example on how to write unittests for your skills (with an example of my Audio Hangman skill).
* An older but complete version of my Audio Hangman skill.
* A message board skill that I am currently developing (in the messages.html and messages_v1.py files), please find more information here: https://www.hackster.io/josep-valls/alexa-message-board-324b84 and the demo and reference here: https://s3.amazonaws.com/aws-website-textconsole-a3cnv/messages.html

# What I did:
Check my skills, all based on this template:
* Audio Hangman: https://www.amazon.com/Josep-Valls-Vargas-Audio-Hangman/dp/B01KKZ5TP0/ref=sr_1_1
* Audio Battleship: https://www.amazon.com/Josep-Valls-Vargas-Audio-Battleship/dp/B01KJ91K5U/ref=sr_1_1
* Naughty Dice: https://www.amazon.com/Josep-Valls-Vargas-Naughty-Dice/dp/B01KWW0XEI/ref=sr_1_1
* Posted Messages: https://www.amazon.com/Josep-Valls-Vargas-Posted-Messages/dp/B01N8YM05O/ref=sr_1_2

# What I learned:
* Use Amazon's intents but translate them to your actions. For example, I translate both StopIntent and CancelIntent to do_cancel. See get_service_translation_layer().
* Use a finite state machine to keep track of what is going on and remap actions accordingly. For example, when the user is playing, do_cancel may prompt the user if they really want to exit. While in the exit prompt, do_cancel may go back to playing. See get_fst() or visit the project page for the Posted Messages skill for more information on how to define a voice interaction using a finite state machine: https://www.hackster.io/josep-valls/alexa-message-board-now-with-slack-324b84#toc-voice-user-interface--vui-6
* Serialize things in a portable way so you can store your state in either the Alexa session object, DynamoDB or somewhere else. A Python dictionary should work (and are stored nicely in a DynamoDB map), just remember to use strings as keys so it can be serialized to json easily. See my serialize() and unserialize() methods.
* DynamoDB is expensive. For multi-turn interactions, don't serialize to DB after every request. Serialize to the session property in your response and persist to DB once you receive a SessionEndedRequest.

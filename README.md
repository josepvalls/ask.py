# ask.py
Single file template, examples and utilities for creating Amazon Alexa's skills (ASK) using Python

## Why?
Amazon provides pretty cool tutorials and examples but most of them are written in Node.js. I thought I'd share my findings with other developers who may prefer Python instead.

## How to get started?
This is intended to work on AWS infrastructure. It uses ASK, Lambda and DynamoDB.
* Setup your skill, when it comes to configuring the endpoint, go to Lambda.
* Create a new lambda using the Python Alexa template. Select *edit code inline* and copy/paste the code from your single-file-template.py file.
* Copy the ARN to the skill.
* Create your Dynamodb table.

## What else is included?
* A little utility to generate utterances given a grammar (with an example of my Audio Hangman and Audio Battleship skills).
* An example on how to write unittests for your skills (with an example of my Audio Hangman skill).
* An older but complete version of my Audio Hangman skill.

# What I did:
Check my skills, all based on this template:
* Audio Hangman: http://alexa.amazon.com/spa/index.html#skills/dp/B01KKZ5TP0/?ref=skill_dsk_skb_sr_0
* Audio Battleship: http://alexa.amazon.com/spa/index.html#skills/dp/B01KJ91K5U/?ref=skill_dsk_skb_sr_0
* Naughty Dice: http://alexa.amazon.com/spa/index.html#skills/dp/B01KWW0XEI/?ref=skill_dsk_skb_sr_0


# What I learned:
* Use Amazon's intents but translate them to your actions. For example, I translate both StopIntent and CancelIntent to do_cancel. See get_service_translation_layer().
* Use a finite state machine to keep track of what is going on and remap actions accordingly. For example, when the user is playing, do_cancel may prompt the user if they really want to exit. While in the exit prompt, do_cancel may go back to playing. See get_fst()
* Serialize things in a portable way so you can store your state in either the Alexa session object, DynamoDB or somewhere else. A Python dictionary should work (and are stored nicely in a DynamoDB map), just remember to use strings as keys so it can be serialized to json easily. See my serialize() and unserialize() methods.
* DynamoDB is expensive. For multi-turn interactions, don't serialize to DB after every request. Serialize to the session property in your response and persist to DB once you receive a SessionEndedRequest.

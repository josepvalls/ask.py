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
* 
## What else is included?
* A little utility to generate utterances given a grammar (with an example of my Audio Hangman and Audio Battleship skills).
* An example on how to write unittests for your skills (with an example of my Audio Hangman skill).
* An older but complete version of my Audio Hangman skill.
* 

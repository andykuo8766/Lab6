#!/usr/bin/python3
# -*- coding: utf8 -*-
from bluedot.btcomm import BluetoothServer
import sys 
try:
    reload         # Python 2
    reload(sys)
    sys.setdefaultencoding('utf8')
except NameError:  # Python 3
    from importlib import reload

import speech_recognition as sr
import tempfile
from gtts import gTTS
from pygame import mixer
import time
import configparser
import urllib
import uuid
import json
import requests

r = sr.Recognizer()

with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source, duration=1)
    print("Say something: ")
    audio=r.listen(source)

def speak(sentence, lang, loops=1):
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts = gTTS(text=sentence, lang=lang)
        tts.save('{}.mp3'.format(fp.name))
        mixer.init()
        mixer.music.load('{}.mp3'.format(fp.name))
        mixer.music.play(loops)
def data_received(data):
    print(data)
    speak(data,'zh-tw')
    message_from_server = "yes"
    s.send(message_from_server)

try:
    print("Google Speech Recognition thinks you said: ")
    sent = r.recognize_google(audio, language="zh-TW")
    print("{}".format(sent))
    query = sent
    lang = 'zh-tw'
    session_id = str( uuid.uuid1() )
    timezone = 'Asia/Taipei'

    config = configparser.ConfigParser()
    config.read('smart_speaker.conf')
    project_id = config.get('dialogflow', 'project_id')
    authorization = config.get('dialogflow', 'authorization')

    headers = {
    "accept": "application/json",
    "authorization": authorization
    }
    url = 'https://dialogflow.googleapis.com/v2/projects/' + project_id +'/agent/sessions/' + session_id + ':detectIntent'
    payload = {"queryInput":{"text":
    {"text":query,"languageCode":lang}},"queryParams":{"timeZone":timezone}}
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    print(payload)
    data = json.loads(response.text)

    print(data)
    queryText = data['queryResult']['queryText']
    fulfillment = data['queryResult']['fulfillmentText']
    confidence = data['queryResult']['intentDetectionConfidence']
    print("Query: {}".format(queryText))
    print("Response: {}".format(fulfillment))
    print("Confidence: {}".format(confidence))
    if fulfillment == "turn_on_light_OK":
        s = BluetoothServer(data_received)
    
    while (True):
        pass
except sr.UnknownValueError:
    print('Google Speech Recognition could not understand audio')
except sr.RequestError as e:
    print('No response from Google Speech Recognition service: {0}'.format(e))


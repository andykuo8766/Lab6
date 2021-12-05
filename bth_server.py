from bluedot.btcomm import BluetoothServer
from importlib import reload

import speech_recognition as sr

import configparser
import uuid
import json
import requests

import tempfile
from gtts import gTTS
from pygame import mixer
import time

def speak(sentence, lang, loops=1):
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts = gTTS(text=sentence, lang=lang)
        tts.save('{}.mp3'.format(fp.name))
        mixer.init()
        mixer.music.load('{}.mp3'.format(fp.name))
        mixer.music.play(loops)

def data_received(data):
    try:
        speak(data, 'zh')
        time.sleep(2)
    except Exception as e:
        print(e)

s = BluetoothServer(data_received)

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

lstate = 0
rstate = 0
r = sr.Recognizer()

def gen_key():
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("工維")
        audio=r.listen(source)

    sent = ""
    try:
        print("Google Speech Recognition thinks you said: ")
        sent = r.recognize_google(audio, language="zh-TW")
        print("{}".format(sent))
    except sr.UnknownValueError:
        print('Google Speech Recognition could not understand audio')
    except sr.RequestError as e:
        print('No response from Google Speech Recognition service: {0}'.format(e))

    if sent == "":
        return "err"
    
    query = sent
    payload = {"queryInput":{"text":
    {"text":query,"languageCode":lang}},"queryParams":{"timeZone":timezone}}
    response = requests.post(url, data=json.dumps(payload), headers=headers)

    data = json.loads(response.text)

    #print(data)
    queryText = data['queryResult']['queryText']
    fulfillment = data['queryResult']['fulfillmentText']
    confidence = data['queryResult']['intentDetectionConfidence']
    #print("Query: {}".format(queryText))
    print("Response: {}".format(fulfillment))
    #print("Confidence: {}".format(confidence))

    global lstate, rstate

    if fulfillment == "left_on":
        lstate = 1
    elif fulfillment == "right_on":
        rstate = 1
    elif fulfillment == "both_on":
        lstate = 1
        rstate = 1
    elif fulfillment == "left_off":
        lstate = 0
    elif fulfillment == "right_off":
        rstate = 0
    elif fulfillment == "both_off":
        lstate = 0
        rstate = 0
    else:
        return "err"

    key = str(lstate) + str(rstate)
    return key

while (True):
    key = gen_key()
    if key != "err":
        s.send(key)


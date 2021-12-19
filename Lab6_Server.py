from bluedot.btcomm import BluetoothServer
import time

import sys 
try:
    reload         # Python 2
    reload(sys)
    sys.setdefaultencoding('utf8')
except NameError:  # Python 3
    from importlib import reload

import speech_recognition as sr

def stt():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        print("Say something: ")
        audio=r.listen(source)

    try:
        print("Google Speech Recognition thinks you said: ")
        sent = r.recognize_google(audio, language="zh-TW")
        print("{}".format(sent))
        voice = "{}".format(sent)
    except sr.UnknownValueError:
        print('Google Speech Recognition could not understand audio')
    except sr.RequestError as e:
        print('No response from Google Speech Recognition service: {0}'.format(e))
    return voice

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
    if data == 'start':
        print('sending control message to Server...')
        order = stt()
        if order == '打開':
            s.send('open pzem')
    else:
        pzem_data = "received PZEM datas from Client: \n" + data
        print(pzem_data)
        speak(pzem_data, 'en')
        print('task completed')

s = BluetoothServer(data_received) 

while (True):
    pass

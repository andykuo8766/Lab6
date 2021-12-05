from bluedot.btcomm import BluetoothServer
import sys 
import speech_recognition as sr
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
    print(data)
    message_from_server = "received " + data
    s.send(message_from_server)
    if data[0] == 'V':
      speak(data, 'en')

s = BluetoothServer(data_received)

try:
    reload         # Python 2
    reload(sys)
    sys.setdefaultencoding('utf8')
except NameError:  # Python 3
    from importlib import reload

r = sr.Recognizer()

with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source, duration=1)
    print("Say something: ")
    audio=r.listen(source)

try:
    print("Google Speech Recognition thinks you said: ")
    sent = r.recognize_google(audio, language="zh-TW")
    print("{}".format(sent))
    s.send("{}".format(sent))
    time.sleep(20)
except sr.UnknownValueError:
    print('Google Speech Recognition could not understand audio')
except sr.RequestError as e:
    print('No response from Google Speech Recognition service: {0}'.format(e))
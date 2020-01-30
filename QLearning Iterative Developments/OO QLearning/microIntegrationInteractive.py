import speech_recognition as sr
import cozmo
import threading
import sys
import asyncio
import time

class voiceIntegration():

   def __init__(self):
        self.speech = ""
        self.action = False
        self.clearSpeech = False
        self.QMove= [[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        self.QStop = [0,0]
        self.sleepTime = 0
        self.running = True

   async def voiceComms(self):
        self.speech = ""
        r = sr.Recognizer()
        mic = sr.Microphone()
        with mic as source:
            print("Please speak FOR THE SCORE")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
            try:
                print("Time to recog SCORE")
                self.speech = r.recognize_google(audio)
                self.clearSpeech = True
                print(self.speech)
            except sr.UnknownValueError:
                self.clearSpeech = False
                print("Not understood error value, try again please")
            except sr.RequestError:
                self.clearSpeech = False
                print("REQ Not understood, try again please")
            except asyncio.TimeoutError:
                self.clearSpeech = False
                print("Timed out")

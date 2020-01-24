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
        self.moveRewards = [[2,-0.5,-2,-5],[-1,0,0.5,-5],[-2.5,-1,1,-5]]
        self.stopRewards =[2,-2]
        self.QStop = [0,0]
        self.sleepTime = 0

   def voiceComms(self):
        while True:
            r = sr.Recognizer()
            mic = sr.Microphone()
            with mic as source:
                print("Please speak")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
                try:
                    self.speech = r.recognize_google(audio)
                    print("Data taken in")
                    self.clearSpeech = True
                    print(self.speech)
                    if "Move".lower() in self.speech.lower() or "Stop".lower() in self.speech.lower():
                        time.sleep(self.sleepTime)
                        self.speech = ""
                except sr.UnknownValueError:
                    self.clearSpeech = False
                    print("Not understood, try again please")
                except sr.RequestError:
                    self.clearSpeech = False
                    print("Not understood, try again please")

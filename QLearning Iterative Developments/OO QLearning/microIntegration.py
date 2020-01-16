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
        self.stopThreads = True

   async def voiceCommsActionHw(self, robot: cozmo.robot.Robot):
       await robot.say_text("Hello nice to meet you").wait_for_completed()

   def voiceCommsAction(self):
       cozmo.run_program(self.voiceCommsActionHw)

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
                    time.sleep(20)
                #     cozmo.run_program(self.voiceCommsAction)
            except sr.UnknownValueError:
                self.clearSpeech = False
                print("Not understood, try again please")
            except sr.RequestError:
                self.clearSpeech = False
                print("Not understood, try again please")

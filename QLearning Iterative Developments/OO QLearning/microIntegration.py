import speech_recognition as sr
import cozmo
import threading
import sys
import asyncio
import time

# class voiceIntegration:
#
#    def __init__(self):
#         self.speech = ""
#         self.action = False
#         self.clearSpeech = False

    ##TRYING TO DO IT WITH THE SAME CONNECTION TO COZMO - NOT WORKING ATM
   # async def voiceCommsAction(self,robot:cozmo.robot.Robot):
   #     if self.action:
   #         await robot.say_text("Hello, nice to meet you").wait_for_completed()
   #     else:
   #         print("Sorry address me by name or give me a doable action")
   #
   # def voiceComms(self,loop):
   #     while True:
   #          r = sr.Recognizer()
   #          mic = sr.Microphone()
   #          with mic as source:
   #              print("Please speak")
   #              r.adjust_for_ambient_noise(source)
   #              audio = r.listen(source)
   #              try:
   #                  self.speech = r.recognize_google(audio)
   #                  print("Data taken in")
   #                  self.clearSpeech = True
   #                  print(self.speech)
   #                  if self.clearSpeech and "Cozmo".lower() in self.speech.lower() or "Cosmo".lower() in self.speech.lower():
   #                      self.action = True
   #                      try:
   #                          cozmo.connect_on_loop(loop)
   #                          cozmo.run_program(self.voiceCommsAction)
   #                      except cozmo.ConnectionError as e:
   #                          sys.exit("A connection error occurred: %s" % e)
   #              except sr.UnknownValueError:
   #                  self.clearSpeech = False
   #                  print("Not understood, try again please")
   #              except sr.RequestError:
   #                  self.clearSpeech = False
   #                  print("Not understood, try again please")


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

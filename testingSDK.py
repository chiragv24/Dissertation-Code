import asyncio
import cozmo.util
import time
import cozmo
from cozmo.util import distance_mm
from cozmo.util import speed_mmps
import cozmo.faces
from cozmoclad.clad.externalInterface import messageEngineToGame as messageEngineToGame
from cozmoclad.clad.externalInterface import messageEngineToGame as messageGameToEngine
import speech_recognition as sr
import threading
import multiprocessing
from multiprocessing import Process
from multiprocessing import Pool
from random import randint


_clad_to_engine_anki = messageGameToEngine.Anki
_clad_to_engine_cozmo = messageGameToEngine.Anki.Cozmo
_clad_to_engine_iface = messageGameToEngine.Anki.Cozmo.ExternalInterface
_clad_to_game_anki = messageEngineToGame.Anki
_clad_to_game_cozmo = messageEngineToGame.Anki.Cozmo
_clad_to_game_iface = messageEngineToGame.Anki.Cozmo.ExternalInterface
_clad_enum = _clad_to_engine_cozmo.ExecutableBehaviorType

robot = cozmo.robot.Robot

def moveRobot(robot:cozmo.robot.Robot):
    robot.drive_straight(distance_mm(-300), speed_mmps(100)).wait_for_completed()

def sayText(robot:cozmo.robot.Robot):
    robot.say_text("Good to see that you want to play, what should we do").wait_for_completed()

def voiceComms():
    while True:
        r = sr.Recognizer()
        clip = sr.AudioFile("C:/Users/Chirag/Desktop/Dissertation/Dissertation-Code/Recording.wav")
        with clip as source:
            audio = r.record(source)
            print("data loaded")
            result = r.recognize_google(audio)
            print(result)
            if ("stop" in result and "Cosmo" in result):
                cozmo.run_program(moveRobot)
            else:
                cozmo.run_program(sayText)
#x = threading.Thread(target = voiceComms,args=())

def counter():
    for i in range(10):
        print(i + 10)
#
# y = threading.Thread(target = counter,args=())
# y.start()

if __name__=='__main__':
    x = Process(target=voiceComms)
    x.start()
    y = Process(target=counter)
    y.start()
    x.join()
    y.join()


# print("Total number of threads", threading.active_count())
# print("list of threads: ",threading.enumerate())
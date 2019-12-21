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
from random import randint


_clad_to_engine_anki = messageGameToEngine.Anki
_clad_to_engine_cozmo = messageGameToEngine.Anki.Cozmo
_clad_to_engine_iface = messageGameToEngine.Anki.Cozmo.ExternalInterface
_clad_to_game_anki = messageEngineToGame.Anki
_clad_to_game_cozmo = messageEngineToGame.Anki.Cozmo
_clad_to_game_iface = messageEngineToGame.Anki.Cozmo.ExternalInterface
_clad_enum = _clad_to_engine_cozmo.ExecutableBehaviorType

robot = cozmo.robot.Robot
allActs = [1,2,3,4]

# def kobe(robot:cozmo.robot.Robot):
#         robot.drive_straight(distance_mm(500),speed_mmps(50)).wait_for_completed()
#         robot.say_text("KOBE").wait_for_completed()
#
# def robotMovement(actionNum,robot:cozmo.robot.Robot):
#     if(actionNum == 0):
#         print("HEELLO")
#         robot.drive_straight(distance_mm(-250),speed_mmps(50)).wait_for_completed()
#     elif(actionNum == 1):
#         print("HEEEEEELO2")
#         robot.drive_straight(distance_mm(250),speed_mmps(50)).wait_for_completed()
#     elif(actionNum == 2):
#         print("Hello3")
#         robot.say_text("Hello, how are you doing today?").wait_for_completed()
#
# def nextAction(robot: cozmo.robot.Robot):
#     nextActRand = randint(0,3)
#     nextAct = allActs[nextActRand]
#     indexOfNextAct = allActs.index(nextAct)
#     robotMovement(indexOfNextAct,robot)
#     return indexOfNextAct
#
# cozmo.run_program(nextAction)

# def robotMovement(actionNum,robot:cozmo.robot.Robot):
#     if(actionNum == 0):
#         print("HEELLO")
#         robot.drive_straight(distance_mm(-250),speed_mmps(50)).wait_for_completed()
#     elif(actionNum == 1):
#         print("HEEEEEELO2")
#         robot.drive_straight(distance_mm(250),speed_mmps(50)).wait_for_completed()
#     elif(actionNum == 2):
#         print("Hello3")
#         robot.say_text("Hello, how are you doing today?").wait_for_completed()
#
# def nextAction(robot: cozmo.robot.Robot):
#     nextActRand = randint(0,3)
#     nextAct = allActs[nextActRand]
#     indexOfNextAct = allActs.index(nextAct)
#     robotMovement(indexOfNextAct,robot)
#     return indexOfNextAct
#
# cozmo.run_program(nextAction)

def voiceComms():
            r = sr.Recognizer()
            clip = sr.AudioFile("C:/Users/Chirag/Desktop/Dissertation/Dissertation-Code/Recording.wav")
            with clip as source:
                audio = r.record(source)
                print("data loaded")
                result = r.recognize_google(audio)
                if ("stop" in result):
                    print("KOBE")
                else:
                    print("CURRY")
                print(result)

#x = threading.Thread(target = voiceComms,args=())
x = multiprocessing.Process(target=voiceComms,args=())
x.start()
x.join()

def counter():
    for i in range(10):
        print(i + 10)
#
# y = threading.Thread(target = counter,args=())
# y.start()

counter()


# print("Total number of threads", threading.active_count())
# print("list of threads: ",threading.enumerate())
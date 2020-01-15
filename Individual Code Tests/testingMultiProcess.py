
import cozmo.util
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

def voiceComms(robot:cozmo.robot.Robot):
    while True:
        print("This is the number of times run " + str(counter))
        r = sr.Recognizer()
        clip = sr.AudioFile("C:/Users/Chirag/Desktop/Dissertation/Dissertation-Code/Recording.wav")
        with clip as source:
            audio = r.record(source)
            print("data loaded")
            result = r.recognize_google(audio)
            print(result)
            if "Cosmo" in result:
                currentState = findCurrentState()
                if "stop" in result:
                    if(currentState == 1):
                        robot.drive_straight(distance_mm(-1000),speed_mmps(50)).wait_for_completed()
                        y.terminate()
                    elif(currentState == 0):
                        y.terminate()
                elif "move" in result:
                    #USE ROBOTMOVEMENT FROM QLEARNING FOR THIS AND THE ONE ABOVE TOO
                    #THINK ABOUT USING THE POSE DISTANCE FROM THE FACE FOR THIS METHOD
                    if(currentState == 1):
                        y.sleep(7)
                        robot.drive_straight(distance_mm(-1000),speed_mmps(50)).wait_for_completed()
                    elif(currentState == 0):
                        y.sleep(7)
                        robot.drive_straight(distance_mm(500),speed_mmps(50)).wait_for_completed()
            if "stop" in result and "Cosmo" in result:
                print("Not in results")
                #cozmo.run_program(moveRobot)
            else:
                print("In result")
                #cozmo.run_program(sayText)

def counter():
    for i in range(100):
        print(i * i)

if __name__=='__main__':
    x = Process(target=voiceComms)
    x.start()
    y = Process(target=counter)
    y.start()
    x.join()
    y.join()
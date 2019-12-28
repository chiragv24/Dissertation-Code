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

def moveRobot(robot:cozmo.robot.Robot):
    robot.drive_straight(distance_mm(-300), speed_mmps(100)).wait_for_completed()

def sayText(robot:cozmo.robot.Robot):
    robot.say_text("Good to see that you want to play, what should we do").wait_for_completed()

# def voiceComms(robot:cozmo.robot.Robot):
#     robot.say_text("You can speak whenever, I will detect it and get back to you")
#     while True:
#         r = sr.Recognizer()
#         with sr.Microphone() as source:
#             audio = r.listen(source)
#             speech = r.recognize_google(audio)
#             if "Cosmo" in speech:
#                 if "Stop" in speech:
#                     #KILL THE THREAD
#                 elif "Move" in speech:
#                     #CHECK THE STATE AND MOVE TO THE OPPOSITE ONE


#YOU WILL NEED A ROBOT FOR THIS ONE WHEN INTEGRATING INTO THE QLEARN ALGO
def voiceComms(robot:cozmo.robot.Robot):
    while True:
        r = sr.Recognizer()
        clip = sr.AudioFile("C:/Users/Chirag/Desktop/Dissertation/Dissertation-Code/Recording.wav")
        with clip as source:
            audio = r.record(source)
            print("data loaded")
            result = r.recognize_google(audio)
            print(result)
            robot.say_text("This is what you said right? " + result).wait_for_completed()
            return result
            #if "Cosmo" in result:
            #     currentState = findCurrentState()
            #     if "stop" in result:
            #         if(currentState == 1):
            #             robot.drive_straight(distance_mm(-1000),speed_mmps(50)).wait_for_completed()
            #             y.terminate()
            #         elif(currentState == 0):
            #             y.terminate()
            #     elif "move" in result:
            #         #USE ROBOTMOVEMENT FROM QLEARNING FOR THIS AND THE ONE ABOVE TOO
            #         #THINK ABOUT USING THE POSE DISTANCE FROM THE FACE FOR THIS METHOD
            #         if(currentState == 1):
            #             y.sleep(7)
            #             robot.drive_straight(distance_mm(-1000),speed_mmps(50)).wait_for_completed()
            #         elif(currentState == 0):
            #             y.sleep(7)
            #             robot.drive_straight(distance_mm(500),speed_mmps(50)).wait_for_completed()
            # if "Cosmo" in result:
            #     if "stop" in result:
            #         print("Kobe")
            #         y.terminate()
            #     elif "well" in result:
            #         print("LBJ")
            #         y.sleep(7)
            #         print("KobeWins")
            #     #cozmo.run_program(moveRobot)
            # else:
            #     print("Neither options have been said by the user")
            #     #cozmo.run_program(sayText)

def counter():
    for i in range(1000):
        print(i)

if __name__=='__main__':
    x = Process(target=cozmo.run_program(voiceComms))
    x.start()
    y = Process(target=counter)
    y.start()

# if __name__=='__main__':
#     counter = 0
#     x = Process(target=voiceComms)
#     x.start()
#     y = Process(target=counter)
#     y.start()
#     if counter > 0:
#         if "Cosmo" in x:
#             if "stop" in x:
#                 y.terminate()
#             elif "well" in x:
#                 y.sleep(5)
#         else:
#             print("DUMBAAS")
#     x.join()
#     y.join()
#     counter = counter+1
#     print(counter)

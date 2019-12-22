import asyncio
import cozmo.util
import time
import cozmo
from cozmo.util import distance_mm, speed_mmps
import cozmo.faces
from cozmoclad.clad.externalInterface import messageEngineToGame as messageEngineToGame
from cozmoclad.clad.externalInterface import messageEngineToGame as messageGameToEngine
import speech_recognition as sr
import threading

_clad_to_engine_anki = messageGameToEngine.Anki
_clad_to_engine_cozmo = messageGameToEngine.Anki.Cozmo
_clad_to_engine_iface = messageGameToEngine.Anki.Cozmo.ExternalInterface
_clad_to_game_anki = messageEngineToGame.Anki
_clad_to_game_cozmo = messageEngineToGame.Anki.Cozmo
_clad_to_game_iface = messageEngineToGame.Anki.Cozmo.ExternalInterface
_clad_enum = _clad_to_engine_cozmo.ExecutableBehaviorType

def hcscenario1(robot: cozmo.robot.Robot):

    print("Press CTRL-C to quit")
    face = None
    while True:
        if not robot.head_angle == cozmo.robot.MAX_HEAD_ANGLE:
            robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
        if face and face.is_visible:
            robot.say_text("Hello, how are you?").wait_for_completed()
            robot.enable_facial_expression_estimation(True)
            if not _clad_to_game_anki.Vision.FacialExpression == _clad_to_game_anki.Vision.FacialExpression.Happiness:
                robot.say_text("Please cheer up, it would make me so happy, please play with me").wait_for_completed()
                robot.play_anim_trigger(cozmo.anim.Triggers.MajorWin).wait_for_completed()
            else:
                robot.say_text("Good to see that you are happy today").wait_for_completed()
        else:
            try:
                face = robot.world.wait_for_observed_face(timeout=30)
            except asyncio.TimeoutError:
                print("Didn't find a face.")
                return

        time.sleep(.1)

def hcscenario2(robot: cozmo.robot.Robot):
    robot.move_lift(-3)
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
    face = None
    proxemicZone = float(1220)
    while True:
        if face and face.is_visible:
            for face in robot.world.visible_faces:
                if face.pose.position.x < proxemicZone:
                    robot.say_text("My bad I will move back").wait_for_completed()
                    distanceToDrive = proxemicZone - face.pose.position.x
                    robot.drive_straight(distance_mm(-distanceToDrive),speed_mmps(50)).wait_for_completed()
                else:
                    robot.say_text("Good I'm not too close")
        try:
            robot.say_text("Sorry can't see you, 10 seconds to find you").wait_for_completed()
            face = robot.world.wait_for_observed_face(timeout=10)
        except asyncio.TimeoutError:
            print("Face not found")
            return

def hcscenario3(robot: cozmo.robot.Robot):
        r = sr.Recognizer()
        clip = sr.AudioFile("C:/Users/Chirag/Desktop/Dissertation/Dissertation-Code/Recording.wav")
        with clip as source:
            audio = r.record(source)
            print("data loaded")
            result = r.recognize_google(audio)
            print(result)
            if("stop" in result and "Cosmo" in result):
                robot.drive_straight(distance_mm(-300), speed_mmps(100)).wait_for_completed()
            else:
                robot.say_text("Good to see that you want to play, what should we do").wait_for_completed()

# def voiceRecog():
#     r = sr.Recognizer()
#     clip = sr.AudioFile("C:/Users/Chirag/Desktop/Dissertation/Dissertation-Code/Recording.wav")
#     with clip as source:
#         audio = r.record(source)
#         print("data loaded")
#         result = r.recognize_google(audio)
#         if ("stop" in result):
#             print("KOBE")
#         else:
#             print("CURRY")
#         print(result)

# voiceThread = threading.Thread(target=hcscenario3,args=(1,))
# voiceThread.start()

cozmo.run_program(hcscenario2)
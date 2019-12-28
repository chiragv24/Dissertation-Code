import numpy as np
from random import randint


import asyncio
import cozmo.util
from cozmo import world
import time
from cozmo.util import Pose
import cozmo
from cozmo.util import distance_mm, speed_mmps
import cozmo.faces
from cozmoclad.clad.externalInterface import messageEngineToGame as messageEngineToGame
from cozmoclad.clad.externalInterface import messageEngineToGame as messageGameToEngine

_clad_to_engine_anki = messageGameToEngine.Anki
_clad_to_engine_cozmo = messageGameToEngine.Anki.Cozmo
_clad_to_engine_iface = messageGameToEngine.Anki.Cozmo.ExternalInterface
_clad_to_game_anki = messageEngineToGame.Anki
_clad_to_game_cozmo = messageEngineToGame.Anki.Cozmo
_clad_to_game_iface = messageEngineToGame.Anki.Cozmo.ExternalInterface
_clad_enum = _clad_to_engine_cozmo.ExecutableBehaviorType



# def testingPose(robot:cozmo.robot.Robot):
#     robot.move_lift(-3)
#     robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
#     face = None
#     while True:
#         if face and face.is_visible:
#             for face in robot.world.visible_faces:
#                 print(str(face.pose.position.x))

def test2(robot:cozmo.robot.Robot):
    robot.move_lift(-3)
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
    face = None
    firstFace = None
    count = 0
    while True:
        if face and face.is_visible:
            for face in robot.world.visible_faces:
                # count = count+1
                # if(count==1):
                #     firstFace = face
                #
                # print("DISTANCE " + str(robot.pose.define_pose_relative_this(firstFace.pose).position.x))
                #
                # if robot.pose.define_pose_relative_this(firstFace.pose).position.x < float(350) and robot.pose.define_pose_relative_this(firstFace.pose).position.x > float(150):
                #     robot.say_text("I'm currently in the optimal state").wait_for_completed()
                #     currentState = 2
                # elif robot.pose.define_pose_relative_this(firstFace.pose).position.x > float(350):
                #     robot.say_text("I´m currently in the far state").wait_for_completed()
                #     currentState = 0
                # else:
                #     robot.say_text("I'm currently in the close state").wait_for_completed()
                #     currentState = 1

                print("This is the distance from the human " + str(face.pose.position.x))

                if face.pose.position.x < float(350) and face.pose.position.x > float(150):
                    robot.say_text("Optimal state").wait_for_completed()
                elif face.pose.position.x > float(350):
                    robot.say_text("Far state").wait_for_completed()
                else:
                    robot.say_text("Close state").wait_for_completed()


                # print("Is this always the same face instance " + str(face))
                # print("RELATIVE TO FIRST " + str(robot.pose.define_pose_relative_this(firstFace.pose)))
                # print("THIS IS THE DISTANCE " + str(face.pose.position.x))
                # print()
        try:
            robot.say_text("Sorry, I couldn´t find your face, 10 seconds to do it").wait_for_completed()
            face = robot.world.wait_for_observed_face(timeout=10)
        except asyncio.TimeoutError:
            robot.say_text("Sorry, it will have to be next time").wait_for_completed()
            print("Face not found")
            return

cozmo.run_program(test2, use_viewer=True)

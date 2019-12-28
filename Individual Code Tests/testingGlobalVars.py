import asyncio
import cozmo.util
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

currentState = 0

def hcscenario2(robot: cozmo.robot.Robot):
    face = None
    proxemicZone = float(700)
    while True:
        if face and face.is_visible:
            for face in robot.world.visible_faces:
                if face.pose.position.x < proxemicZone:
                    robot.say_text("Saw you, I´m moving back").wait_for_completed()
                    currentState = 1
                    return currentState
                else:
                    robot.say_text("Saw you, I'm moving ahead").wait_for_completed()
                    currentState = 0
                    return currentState
        try:
            robot.say_text("Sorry can't see you, 10 seconds to find you").wait_for_completed()
            face = robot.world.wait_for_observed_face(timeout=10)
        except asyncio.TimeoutError:
            print("Face not found")
            return


def findCurrentState(robot: cozmo.robot.Robot):
    moveRobotHead(robot)
    face = hcscenario2(robot)
    print(face)
    return face

def moveRobotHead(robot:cozmo.robot.Robot):
    robot.move_lift(-3)
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()

cozmo.run_program(findCurrentState,use_viewer=True)
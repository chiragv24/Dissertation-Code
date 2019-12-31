import numpy as np
from random import randint
import cozmo.util
import time
from cozmo.util import Pose
import cozmo
from cozmo.util import distance_mm, speed_mmps
import math
import cozmo.faces
import cozmo.behavior
from cozmoclad.clad.externalInterface import messageEngineToGame as messageEngineToGame
from cozmoclad.clad.externalInterface import messageEngineToGame as messageGameToEngine

_clad_to_engine_anki = messageGameToEngine.Anki
_clad_to_engine_cozmo = messageGameToEngine.Anki.Cozmo
_clad_to_engine_iface = messageGameToEngine.Anki.Cozmo.ExternalInterface
_clad_to_game_anki = messageEngineToGame.Anki
_clad_to_game_cozmo = messageEngineToGame.Anki.Cozmo
_clad_to_game_iface = messageEngineToGame.Anki.Cozmo.ExternalInterface
_clad_enum = _clad_to_engine_cozmo.ExecutableBehaviorType

#Where 0 = is upright and 1 = turned round
states = [0,1]
rewards = [[-0.5,1.5],[-1.5,1]]
#Learning Rate
gamma = 0.8
Q = [[0,0],[0,0]]
initState = 0
nextActionIndex = 0

def robotMoves(robot:cozmo.robot.Robot):
    while True:
        m = robot.pose_pitch.degrees
        u = robot.pose_angle.degrees
        print("ROTATION AROUND " + str(u))
        print("UP AND DOWN " + str(m))
        time.sleep(10)

#cozmo.run_program(robotMoves)

def availActions(state):
    currentStateRow = rewards[state][:]
    print(currentStateRow)
    return currentStateRow

allActs = availActions(initState)
#
def findCurrentState(robot: cozmo.robot.Robot):
    robot.enable_all_reaction_triggers(True)
    angle = str(robot.pose_pitch.degrees)

    if robot.is_picked_up and 90 < float(angle) < 180:
        currentState = 1
    else:
        currentState = 0
    return currentState

def robotMovement(actionNum,robot:cozmo.robot.Robot):
    if(actionNum == 1):
        robot.play_anim("anim_reacttocliff_faceplantroll_02").wait_for_completed()
        time.sleep(5)
    else:
        robot.say_text("I don´t like to be flipped, please rotate me around if I am turned").wait_for_completed()

def nextAction(robot:cozmo.robot.Robot):
    nextActRand = randint(0,1)
    nextAct = allActs[nextActRand]
    indexOfNextAct = allActs.index(nextAct)
    robotMovement(indexOfNextAct,robot)
    global nextActionIndex
    nextActionIndex = indexOfNextAct

def update(currentState,action,gamma):
    Q[currentState][action] = round(rewards[currentState][action] + gamma * np.max(rewards[currentState][:]),2)

def trainCozmo(robot:cozmo.robot.Robot):
    for i in range (5):
        currentState = findCurrentState(robot)
        print("THIS IS THE CURRENTSTATE " + str(currentState))
        nextAction(robot)
        update(currentState, nextActionIndex, gamma)
        print(str(Q))

cozmo.run_program(trainCozmo)
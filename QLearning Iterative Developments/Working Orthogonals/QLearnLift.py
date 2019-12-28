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

#Where 0 = on table and 1 = lifted
states = [0,1]
rewards = [[-0.5,1.5],[-1.5,1]]
#Learning Rate
gamma = 0.8
Q = [[0,0,0,0],[0,0,0,0]]
initState = 0
nextActionIndex = 0


def availActions(state):
    currentStateRow = rewards[state][:]
    print(currentStateRow)
    return currentStateRow

allActs = availActions(initState)

def findCurrentState(robot: cozmo.robot.Robot):
    if robot.is_picked_up:
        currentState = 1
    else:
        currentState = 0
    return currentState

def robotMovement(actionNum,robot:cozmo.robot.Robot):
    counter = 0
    if(actionNum == 0):
        robot.move_lift(3.0)
        time.sleep(0.5)
        robot.move_lift(-3.0)
    else:
        robot.say_text("I like to be on the table, please don´t lift me").wait_for_completed()

def nextAction(robot:cozmo.robot.Robot):
    nextActRand = randint(0,1)
    nextAct = allActs[nextActRand]
    indexOfNextAct = allActs.index(nextAct)
    robotMovement(indexOfNextAct,robot)
    global nextActionIndex
    nextActionIndex = indexOfNextAct

def trainCozmo(robot:cozmo.robot.Robot):
    for i in range (5):
        currentState = findCurrentState(robot)
        nextAction(robot)
        update(currentState, nextActionIndex, gamma)

def update(currentState,action,gamma):
    Q[currentState][action] = round(rewards[currentState][action] + gamma * np.max(rewards[currentState][:]),2)

cozmo.run_program(trainCozmo)
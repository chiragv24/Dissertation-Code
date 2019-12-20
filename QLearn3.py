import numpy as np
from random import randint


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

#Reference to Cozmo throughout the whole program
robot = cozmo.robot.Robot

#Where 1 = far dist, 2 = close dist
states = [0,1]
#Where 1 = forward, 2 = backward, 3 = greet, 4 = idle
actions = [0,1,2,3]
#Random values assigned as of now
rewards = [[-1.1,-2.1,-1.5,-2],[-2.1,-0.1,0.5,0]]
#Learning Rate
gamma = 0.8
Q = [[0,0,0,0],[0,0,0,0]]
initState = 0

def availActions(state):
    currentStateRow = rewards[state][:]
    print(currentStateRow)
    return currentStateRow

allActs = availActions(initState)

def robotMovement(actionNum,robot:cozmo.robot.Robot):
    if(actionNum == 0):
        print("HEELLO")
        robot.drive_straight(distance_mm(-250),speed_mmps(50)).wait_for_completed()
    elif(actionNum == 1):
        print("HEEEEEELO2")
        robot.drive_straight(distance_mm(250),speed_mmps(50)).wait_for_completed()
    elif(actionNum == 2):
        print("Konne")
        robot.say_text("Hello how are you doing today?").wait_for_completed()

def nextAction(robot: cozmo.robot.Robot):
    print(allActs)
    nextActRand = randint(0,3)
    nextAct = allActs[nextActRand]
    indexOfNextAct = allActs.index(nextAct)
    robotMovement(indexOfNextAct,robot)
    print(indexOfNextAct)
    return indexOfNextAct

print(robot)
#nextAct = nextAction(robot)
nextAct = cozmo.run_program(nextAction)
print(nextAct)

#Updating Q values
def update(currentState,action,gamma):
    print("currentstate in the method update")
    print(currentState)
    print(np.max(rewards[currentState][:]))
    Q[currentState][action] = round(rewards[currentState][action] + gamma * np.max(rewards[currentState][:]),2)
    return currentState

update(initState,nextAct,gamma)

#Training the model
for i in range (50):
    currentStateRand = randint(0,1)
    action = cozmo.run_program(nextAction)
    #action = nextAction(actions,robot)
    eval = update(currentStateRand, action, gamma)
    print(Q)

# Testing the model this time, commenting for robot interfacing

# def finalTest(robot:cozmo.robot.Robot):
#     sum = 0
#     initState = 0
#     for i in range (15):
#         print("This is the testing stage " + str(i))
#         bestVal= np.max(Q[initState][:])
#         sum+=bestVal
#         nextStep = Q[initState].index(bestVal)
#         robotMovement(nextStep,robot)
#         if(nextStep == 0):
#             nextStep = 1
#         elif(nextStep == 1):
#             nextStep = 0
#         elif(nextStep!= 1 or nextStep!=0):
#             nextStep = initState
#         initState = nextStep

print("THIS IS THE FINAL RESULT")
print(Q)
print(sum)
robot.say_text("Hello how are you doing today mate").wait_for_completed()
































# def update(state,action):
#     print("Before")
#     print(rewards)
#     print(rewards[state][action])
#     rewards[state][action] = rewards[state][action] + exploreVExploit * (reward + gamma * np.max(rewards[state][:])) - rewards[state][action]
#     print("After")
#     print(rewards)




#exploration v exploitation
# gamma = 0.5
# learnR = 0.5
# epochs = 5



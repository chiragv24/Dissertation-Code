import numpy as np
from random import randint


import asyncio
import cozmo.util
from cozmo import world
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
#Where 0 = far dist, 1 = close dist
states = [0,1]
#Where 1 = forward, 2 = backward, 3 = greet, 4 = idle
actions = [0,1,2,3]
#Random values assigned as of now
rewards = [[-1.1,-2.1,-1.5,-2],[-2.1,-0.1,0.5,0]]
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

def robotMovement(actionNum,robot:cozmo.robot.Robot):
    if(actionNum == 0):
        robot.say_text("I´m moving back now")
        robot.drive_straight(distance_mm(-250),speed_mmps(50)).wait_for_completed()
    elif(actionNum == 1):
        robot.say_text("I'm moving forward now")
        robot.drive_straight(distance_mm(250),speed_mmps(50)).wait_for_completed()
    elif(actionNum == 2):
        robot.say_text("Hello how are you doing today?").wait_for_completed()
    else:
        robot.say_text("I'm not moving this time").wait_for_completed()

def nextAction(robot: cozmo.robot.Robot):
    nextActRand = randint(0,3)
    nextAct = allActs[nextActRand]
    indexOfNextAct = allActs.index(nextAct)
    robotMovement(indexOfNextAct,robot)
    global nextActionIndex
    nextActionIndex = indexOfNextAct

#Updating Q values
def update(currentState,action,gamma):
    Q[currentState][action] = round(rewards[currentState][action] + gamma * np.max(rewards[currentState][:]),2)

def findCurrentState(robot: cozmo.robot.Robot):
    moveRobotHead(robot)
    face = searchForFace(robot)
    return face

def searchForFace(robot: cozmo.robot.Robot):
    face = None
    while True:
        if face and face.is_visible:
            for face in robot.world.visible_faces:
                print("THIS IS THE DISTANCE " + str(face.pose.position.x))
                if face.pose.position.x < float(200):
                    robot.say_text("I'm currently in the close state").wait_for_completed()
                    currentState = 1
                else:
                    robot.say_text("I'm currently in the far state").wait_for_completed()
                    currentState = 0
                return currentState
        try:
            robot.say_text("Sorry, I couldn´t find your face, 10 seconds to do it").wait_for_completed()
            face = robot.world.wait_for_observed_face(timeout=10)
        except asyncio.TimeoutError:
            robot.say_text("Sorry, it will have to be next time").wait_for_completed()
            print("Face not found")
            return

def moveRobotHead(robot:cozmo.robot.Robot):
    robot.move_lift(-3)
    robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()

def trainCozmo(robot:cozmo.robot.Robot):
#Training the model
    for i in range (10):
        ##FINDS THE DISTANCE WITH THE HUMAN USING POSE
        currentState = findCurrentState(robot)
        print(currentState)
        #currentStateRand = randint(0,1)
        nextAction(robot)
        update(currentState, nextActionIndex, gamma)

cozmo.run_program(trainCozmo,use_viewer=True)




#
# if __name__=='__main__':
#     cozmoThread = Process(target=trainCozmo)
#     cozmoThread.start()
#     listenerThread = Process(target=hcscenario3,args=(robot))
#     listenerThread.start()
#     cozmoThread.join()
#     listenerThread.join()
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



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
#Where 0 = far dist, 1 = med dist, 2 = close dist
states = [0,1,2]
#Where 1 = forward, 2 = backward, 3 = greet, 4 = idle
actions = [0,1,2,3]
#Random values assigned as of now
rewards = [[-1.1,-2.1,-1.5,-2],[-0.1,-0.1,1.5,0], [-2.1,-0.1,0.5,0]]
#Learning Rate
gamma = 0.8
Q = [[0,0,0,0],[0,0,0,0],[0,0,0,0]]
initState = 0
nextActionIndex = 0
initCount = 0
greetedState = False

def availActions(state):
    assert state >= 0 and state < len(rewards),"Sorry the state is not valid"
    currentStateRow = rewards[state][:]
    return currentStateRow

allActs = availActions(initState)

def robotMovement(actionNum,facialExp,currentState,robot:cozmo.robot.Robot):
    if(currentState == 0 and facialExp == "happy"):
        robot.say_text("I will stay here until you tell me to move").wait_for_completed()
    elif(currentState == 2 and facialExp == "happy"):
        print("Moved backwards")
        robot.say_text("I'm so happy you want me here").wait_for_completed()
    elif(actionNum == 0):
        print("Moved backwards")
        robot.say_text("I´m moving back now").wait_for_completed()
        robot.drive_straight(distance_mm(-100),speed_mmps(50)).wait_for_completed()
    elif(actionNum == 1):
        print("Moved forward")
        robot.say_text("I'm moving forward now").wait_for_completed()
        robot.drive_straight(distance_mm(100),speed_mmps(50)).wait_for_completed()
    elif(actionNum == 2):
        print("Greeted")
        robot.say_text("Hello how are you doing today?").wait_for_completed()
        global greetedState
        greetedState = True
    else:
        print("idle")
        robot.say_text("I'm not moving this time").wait_for_completed()

def facialExpressionEstimate(robot:cozmo.robot.Robot):
    face = None
    while True:
        if face and face.is_visible:
            robot.enable_facial_expression_estimation(True)
            return face.expression
        else:
            try:
                face = robot.world.wait_for_observed_face(timeout=10)
            except asyncio.TimeoutError:
                robot.say_text("Sorry it will have to be next time").wait_for_completed()
                print("Didn't find a face.")
                return


def nextAction(currentState,robot: cozmo.robot.Robot):
    nextActRand = randint(0,3)
    nextAct = allActs[nextActRand]
    indexOfNextAct = allActs.index(nextAct)
    facialExp = facialExpressionEstimate(robot)
    robotMovement(indexOfNextAct,facialExp,currentState,robot)
    global nextActionIndex
    nextActionIndex = indexOfNextAct

#Updating Q values
def update(currentState,action,gamma):
    global greetedState
    greet = greetedState
    Q[currentState][action] = round(rewards[currentState][action] + gamma * np.max(rewards[currentState][:]),2)

def findCurrentState(robot: cozmo.robot.Robot):
    moveRobotHead(robot)
    face = searchForFace(robot)
    return face

def searchForFace(robot: cozmo.robot.Robot):
    face = None
    initPose = None
    count = 0
    while True:
        if face and face.is_visible:
            for face in robot.world.visible_faces:

                print()
                print("Is this always the same face instance " + str(face))
                print("THIS IS THE DISTANCE " + str(face.pose.position.x))
                robot.pose.define_pose_relative_this(face.pose)

                if face.pose.position.x < float(350) and face.pose.position.x > float(150):
                    robot.say_text("I'm currently in the optimal state").wait_for_completed()
                    currentState = 1
                elif face.pose.position.x > float(350):
                    robot.say_text("I´m currently in the far state").wait_for_completed()
                    currentState = 0
                else:
                    robot.say_text("I'm currently in the close state").wait_for_completed()
                    currentState = 2
                return currentState
        else:
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
    for i in range (2):
        ##FINDS THE DISTANCE WITH THE HUMAN USING POSE
        currentState = findCurrentState(robot)
        nextAction(currentState,robot)
        update(currentState, nextActionIndex, gamma)

cozmo.run_program(trainCozmo,use_viewer=False)

print("THIS IS THE FINAL RESULT")
print(Q)


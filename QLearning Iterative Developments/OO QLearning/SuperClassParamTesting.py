import abc
import cozmo
from cozmo.util import distance_mm, speed_mmps
import numpy as np
from random import randint
import asyncio
import time


class QLearnSuperClass(abc.ABC):

    def __init__(self):
        self.initState = 0
        self.gamma = 0.8
        self.nextActIndex = 0
        self.Q = []
        self.states = []
        self.actions = []
        self.rewards = []

    @abc.abstractmethod
    def allActions(self,state):
        pass

    @abc.abstractmethod
    def robotMovement(self,*args,**kwargs):
        pass

    @abc.abstractmethod
    def nextAction(self,*args,**kwargs):
        pass

    @abc.abstractmethod
    def update(self,currentState,action,gamma):
        pass

    @abc.abstractmethod
    def findCurrentState(self):
        pass

    @abc.abstractmethod
    def trainCozmo(self):
        pass


################FIRST ORTHOGONAL##########################################################################################


class QLearnDistOrthogonal(QLearnSuperClass):

    nextActionIndex = 0

    def __init__(self):
        super(QLearnDistOrthogonal, self).__init__()
        self.actions = [0,1,2,3]
        self.rewards = [[-1.1,-2.1,-1.5,-2],[-0.1,-0.1,1.5,0], [-2.1,-0.1,0.5,0]]
        self.Q = [[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        self.states = [0,1,2]
        self.gamma = 0.8
        self.initState = 0
        self.nextActIndex = 0
        self.currentState = 0
        self.facialExpression = ""
        self.robotHeadPosition = 0
        self.robotLiftPosition = 0
        self.robotHeadPositionBef = 0
        self.robotLiftPositionBef = 0
        self.distanceFromFace = 0

    def allActions(self,state):
        assert state >= 0 and state < len(self.rewards), "Sorry the state is not valid"
        currentStateRow = self.rewards[state][:]
        return currentStateRow

    def robotSayTextIdle(self,robot:cozmo.robot.Robot):
        robot.say_text("I'm happy to stay here until you tell me to move").wait_for_completed()

    def robotMoveBack(self,robot:cozmo.robot.Robot):
        robot.drive_straight(distance_mm(-100), speed_mmps(50)).wait_for_completed()

    def robotMoveFront(self,robot:cozmo.robot.Robot):
        robot.drive_straight(distance_mm(100), speed_mmps(50)).wait_for_completed()

    def robotGreet(self,robot:cozmo.robot.Robot):
        robot.say_text("Hello how are you doing today?").wait_for_completed()

    def robotMovement(self, actionNum, facialExp, currentState):

        assert 0 <= actionNum <= 3
        assert currentState == 0 or currentState == 1

        allExps = ["Unknown","Happy","Sad","Neutral","Surprised","Angry"]
        facial = False

        for i in range(allExps.__len__()):
            if facialExp.lower() == allExps[i].lower():
                facial = True
        assert facial == True


        if (currentState == 0 and facialExp == "happy"):
            print("staying far")
            cozmo.run_program(self.robotSayTextIdle)
            return "staying far"

        elif (currentState == 2 and facialExp == "happy"):
            print("staying close")
            cozmo.run_program(self.robotSayTextIdle)
            return "staying close"

        elif (actionNum == 0):
            print("Moving backwards")
            cozmo.run_program(self.robotMoveBack)
            return "moving backwards"

        elif (actionNum == 1):
             print("Moved forward")
             cozmo.run_program(self.robotMoveBack)
             return "moving forwards"

        elif (actionNum == 2):
            print("Greeted")
            cozmo.run_program(self.robotGreet)
            return "greeting"

        else:
            print("idle")
            return "idle"

    def nextAction(self):
        nextActRand = randint(0,3)
        #self.facialExpressionEstimate()
        #self.robotMovement(nextActRand, self.facialExpression, self.currentState)
        global nextActionIndex
        nextActionIndex = nextActRand
        return nextActionIndex

    def update(self,currentState,action,gamma):
        assert 0 <= currentState <= 2
        assert 0 <= action <= 3
        assert 0 <= gamma <= 1
        self.Q[currentState][action] = round(self.rewards[currentState][action] + gamma * np.max(self.rewards[currentState][:]), 2)

    def findCurrentState(self):
        self.moveRobotHead()
        face = self.searchForFace()
        return face

    def trainCozmo(self):
        # Training the model
        for i in range(2):
            self.findCurrentState()
            act = self.nextAction()
            self.facialExpressionEstimate()
            self.robotMovement(act, self.facialExpression, self.currentState)
            self.update(self.currentState, nextActionIndex, self.gamma)

    def robotMovingHead(self,robot:cozmo.robot.Robot):
        self.robotHeadPositionBef = robot.head_angle
        self.robotLiftPositionBef = robot.lift_position.height.distance_mm

        if robot.lift_position != cozmo.robot.MIN_LIFT_HEIGHT:
            self.robotLiftPosition = cozmo.robot.MIN_LIFT_HEIGHT.distance_mm
            robot.move_lift(-3)
        if robot.head_angle!=cozmo.robot.MAX_HEAD_ANGLE:
            self.robotHeadPosition = cozmo.robot.MAX_HEAD_ANGLE
            robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
        m = self.robotHeadPosition
        m1 = self.robotLiftPosition

    def moveRobotHead(self):
        cozmo.run_program(self.robotMovingHead)

    def hwSearchFace(self,robot:cozmo.robot.Robot):
        face = None
        while True:
            if face and face.is_visible:
                for face in robot.world.visible_faces:

                    print()
                    print("Is this always the same face instance " + str(face))
                    print("THIS IS THE DISTANCE " + str(face.pose.position.x))
                    robot.pose.define_pose_relative_this(face.pose)

                    self.distanceFromFace = face.pose.position.x

                    if face.pose.position.x < float(350) and face.pose.position.x > float(150):
                        robot.say_text("I'm currently in the optimal state").wait_for_completed()
                        self.currentState = 1
                    elif face.pose.position.x > float(350):
                        robot.say_text("I´m currently in the far state").wait_for_completed()
                        self.currentState = 0
                    else:
                        robot.say_text("I'm currently in the close state").wait_for_completed()
                        self.currentState = 2
                    return self.currentState
            else:
                try:
                    robot.say_text("Sorry, I couldn´t find your face, 10 seconds to do it").wait_for_completed()
                    face = robot.world.wait_for_observed_face(timeout=10)
                except asyncio.TimeoutError:
                    robot.say_text("Sorry, it will have to be next time").wait_for_completed()
                    print("Face not found")
                    return

    def searchForFace(self):
        cozmo.run_program(self.hwSearchFace)

    def hwFacialExpEstimate(self,robot:cozmo.robot.Robot):
        face = None
        while True:
            if face and face.is_visible:
                robot.enable_facial_expression_estimation(True)
                self.facialExpression = face.expression
                return face.expression
            else:
                try:
                    face = robot.world.wait_for_observed_face(timeout=10)
                except asyncio.TimeoutError:
                    robot.say_text("Sorry it will have to be next time").wait_for_completed()
                    print("Didn't find a face.")
                    return

    def facialExpressionEstimate(self):
        cozmo.run_program(self.hwFacialExpEstimate)

m = QLearnDistOrthogonal()
m.moveRobotHead()
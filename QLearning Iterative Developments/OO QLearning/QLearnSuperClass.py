import abc
import cozmo
from cozmo.util import distance_mm, speed_mmps
import numpy as np
from random import randint
import asyncio
import time
import threading


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
    def findCurrentState(self,robot:cozmo.robot.Robot):
        pass

    @abc.abstractmethod
    def trainCozmo(self,robot:cozmo.robot.Robot):
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

    def allActions(self,state):
        assert state >= 0 and state < len(self.rewards), "Sorry the state is not valid"
        currentStateRow = self.rewards[state][:]
        return currentStateRow

    #Let it be in a stochastic state, if this call does not work (not at the moment)
    #allActs = self.allActions(self.initState)

    def robotMovement(self, actionNum, facialExp, currentState, robot: cozmo.robot.Robot):
        if (currentState == 0 and facialExp == "happy"):
            robot.say_text("I will stay here until you tell me to move").wait_for_completed()
        elif (currentState == 2 and facialExp == "happy"):
            print("Moved backwards")
            print(robot)
            robot.say_text("I'm so happy you want me here").wait_for_completed()
        elif (actionNum == 0):
            print("Moved backwards")
            robot.say_text("I´m moving back now").wait_for_completed()
            robot.drive_straight(distance_mm(-150), speed_mmps(50)).wait_for_completed()
        elif (actionNum == 1):
            print("Moved forward")
            robot.say_text("I'm moving forward now").wait_for_completed()
            robot.drive_straight(distance_mm(150), speed_mmps(50)).wait_for_completed()
        elif (actionNum == 2):
            print("Greeted")
            robot.say_text("Hello how are you doing today?").wait_for_completed()
        else:
            print("idle")
            robot.say_text("I'm not moving this time").wait_for_completed()

    def nextAction(self, currentState, robot: cozmo.robot.Robot):
        nextActRand = randint(0,3)
        facialExp = self.facialExpressionEstimate(robot)
        self.robotMovement(nextActRand, facialExp, currentState, robot)
        #THIS CAN BE A PROBLEM
        global nextActionIndex
        nextActionIndex = nextActRand

    def update(self,currentState,action,gamma):
        self.Q[currentState][action] = round(self.rewards[currentState][action] + gamma * np.max(self.rewards[currentState][:]), 2)

    def findCurrentState(self,robot:cozmo.robot.Robot):
        self.moveRobotHead(robot)
        face = self.searchForFace(robot)
        return face

    def trainCozmo(self,robot: cozmo.robot.Robot):
        # Training the model
        for i in range(2):
            ##FINDS THE DISTANCE WITH THE HUMAN USING POSE
            currentState = self.findCurrentState(robot)
            self.nextAction(currentState, robot)
            self.update(currentState, nextActionIndex, self.gamma)
        print(self.Q)

    def moveRobotHead(self,robot:cozmo.robot.Robot):
        robot.move_lift(-3)
        robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()

    def searchForFace(self,robot: cozmo.robot.Robot):
        face = None
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

    def facialExpressionEstimate(self,robot: cozmo.robot.Robot):
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

###################NEW ORTHOGONAL#######################################################################################


class QLearnLiftOrthogonal(QLearnSuperClass):

    nextActionIndex = 0

    def __init__(self):
        super(QLearnLiftOrthogonal, self).__init__()
        self.actions = [0, 1, 2, 3]
        self.rewards = [[-0.5, 1.5], [-1.5, 1]]
        self.Q = [[0, 0, 0, 0], [0, 0, 0, 0]]
        self.states = [0, 1]
        self.gamma = 0.8
        self.initState = 0
        self.nextActIndex = 0
        self.lock = threading.Lock()

    def allActions(self,state):
        currentStateRow = self.rewards[state][:]
        return currentStateRow

    def findCurrentState(self,robot:cozmo.robot.Robot):
        if robot.is_picked_up:
            currentState = 1
        else:
            currentState = 0
        return currentState

    def robotMovement(self,actionNum,robot:cozmo.robot.Robot):
        if (actionNum == 0):
            robot.play_anim("anim_reacttocliff_pickup_01").wait_for_completed()
            print("THIS IS THE PICKED UP ORTHOG")
        else:
            print("THIS IS THE PICKED UP ORTHOG")
            robot.say_text("I like to be on the table, please don´t pick me up").wait_for_completed()

    def nextAction(self,robot:cozmo.robot.Robot):
        nextActRand = randint(0,1)
        self.robotMovement(nextActRand,robot)
        #THIS CAN BE A PROBLEM
        global nextActionIndex
        nextActionIndex = nextActRand

    def trainCozmo(self,robot:cozmo.robot.Robot):
        self.lock.acquire()
        for i in range(1):
            currentState = self.findCurrentState(robot)
            self.nextAction(robot)
            self.update(currentState, nextActionIndex, self.gamma)
        print(self.Q)
        self.lock.release()

    def update(self,currentState,action,gamma):
        self.Q[currentState][action] = round(self.rewards[currentState][action] + gamma * np.max(self.rewards[currentState][:]), 2)


##################THIRD ORTHOGONAL######################################################################################

class QLearnTurnOrthogonal(QLearnSuperClass):

    nextActionIndex = 0

    def __init__(self):
        super(QLearnTurnOrthogonal, self).__init__()
        self.actions = [0, 1]
        self.rewards = [[-0.5, 1.5], [-1.5, 1]]
        self.Q = [[0, 0, 0, 0], [0, 0, 0, 0]]
        self.states = [0, 1]
        self.gamma = 0
        self.initState = 0
        self.lock = threading.Lock()
        self.nextActIndex = 0

    def allActions(self,state):
        currentStateRow = self.rewards[state][:]
        return currentStateRow

    def findCurrentState(self,robot:cozmo.robot.Robot):
        robot.enable_all_reaction_triggers(True)
        angle = str(robot.pose_pitch.degrees)
        if 90 < float(angle) < 180:
            currentState = 1
        else:
            currentState = 0
        return currentState

    def robotMovement(self,actionNum,robot:cozmo.robot.Robot):
        if(actionNum==1):
            print("THIS IS THE TURNED AROUND ORTHOGONAL")
            robot.play_anim("anim_reacttocliff_faceplantroll_02").wait_for_completed()
            time.sleep(5)
        else:
            print("THIS IS THE TURNED AROUND ORTHOGONAL")
            robot.say_text("I don´t like to be flipped, please rotate me around again").wait_for_completed()

    def nextAction(self,robot:cozmo.robot.Robot):
        nextActRand = randint(0,1)
        self.robotMovement(nextActRand,robot)
        global nextActionIndex
        nextActionIndex = nextActRand

    def update(self,currentState,action,gamma):
        self.Q[currentState][action] = round(self.rewards[currentState][action] + gamma * np.max(self.rewards[currentState][:]), 2)

    def trainCozmo(self,robot: cozmo.robot.Robot):
        self.lock.acquire()
        for i in range(1):
            currentState = self.findCurrentState(robot)
            self.nextAction(robot)
            self.update(currentState, nextActionIndex, self.gamma)
        print(self.Q)
        self.lock.release()

###########FOURTH ORTHOGONAL###########################################################################################

class QLearnGreetOrthogonal(QLearnSuperClass):

    nextActionIndex = 0

    def __init__(self):
        super(QLearnGreetOrthogonal, self).__init__()
        self.actions = [0, 1]
        self.rewards = [[-0.5, 1.5], [-1.5, 1]]
        self.Q = [[0, 0, 0, 0], [0, 0, 0, 0]]
        self.states = [0, 1]
        self.gamma = 0
        self.initState = 0
        self.nextActIndex = 0
        self.greeted = False
        self.lock = threading.Lock()

    def allActions(self,state):
        currentStateRow = self.rewards[state][:]
        return currentStateRow

    def randomState(self):
        randomAction = randint(0,1)
        if randomAction == 1:
            self.greeted = False
        else:
            self.greeted = True

    def findCurrentState(self,robot:cozmo.robot.Robot):
        ##Greeted is state 0 and not greeted is state 1
        self.randomState()
        if self.greeted == False:
            currentState = 1
        else:
            currentState = 0
        return currentState

    def robotMovement(self,actionNum,robot:cozmo.robot.Robot):
        if(actionNum==1):
            print("THIS IS THE GREET ORTHOGONAL")
            robot.say_text("Hello how are you doing today?, I´m Cozmo").wait_for_completed()
            self.greeted = True
        else:
            print("THIS IS THE GREET AROUND ORTHOGONAL")
            robot.say_text("Hello again, I´m Cozmo").wait_for_completed()

    def nextAction(self,robot:cozmo.robot.Robot):
        nextActRand = randint(0,1)
        self.robotMovement(nextActRand,robot)
        global nextActionIndex
        nextActionIndex = nextActRand

    def update(self,currentState,action,gamma):
        self.Q[currentState][action] = round(self.rewards[currentState][action] + gamma * np.max(self.rewards[currentState][:]), 2)

    def trainCozmo(self,robot: cozmo.robot.Robot):
        for i in range(1):
            currentState = self.findCurrentState(robot)
            self.nextAction(robot)
            self.update(currentState, nextActionIndex, self.gamma)
        print(self.Q)


##############VOICE RECOG ###########################################3


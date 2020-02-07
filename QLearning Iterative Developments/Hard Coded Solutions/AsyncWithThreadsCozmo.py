import cozmo
import asyncio
from cozmo.util import distance_mm, speed_mmps
from random import randint
import numpy as np
import time
import abc
from threading import Thread
from microIntegration import voiceIntegration

class QLearnSuperClass(abc.ABC):

    def __init__(self):
        self.initState = 0
        self.gamma = 0.8
        self.nextActIndex = 0
        self.Q = []
        self.states = []
        self.actions = []
        self.rewards = []
        self.voice = voiceIntegration()
        self.loop = asyncio.get_event_loop()

    # @abc.abstractmethod
    # def allActions(self,state):
    #     pass

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


class QLearnDistOrthogonal(QLearnSuperClass):

    nextActionIndex = 0

    def _init_(self):
        super(QLearnDistOrthogonal, self).__init__()
        self.actions = [0,1,2,3]
        self.rewards = [[-1.1,-2.1,-1.5,-2],[-0.1,-0.1,1.5,0], [-2.1,-0.1,0.5,0]]
        self.Q = [[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        self.facialRewards = [10, -100]
        self.facialQ = [0, 0]
        self.states = [0, 1, 2]
        self.voice = voiceIntegration()
        self.maxAction = 0
        self.totalScore = 0
        self.rate = 0.3
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

    def startLoop(self,loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeThread(self):
        newLoop = asyncio.new_event_loop()
        t = Thread(target=self.startLoop, args=(newLoop,), daemon=True)
        t.start()
        newLoop.call_soon_threadsafe(self.voice.voiceComms)

    async def voiceMoveHW(self,robot:cozmo.robot.Robot,action):
        await robot.say_text("I'm going to act based on your command now")
        if action == 0:
            await robot.drive_straight(distance_mm(-150), speed_mmps(50)).wait_for_completed()
        elif action == 2:
            await robot.drive_straight(distance_mm(150), speed_mmps(50)).wait_for_completed()
        elif action == 1:
            await robot.say_text("Are you sure you want me to move?").wait_for_completed()
        elif action == 3:
            await robot.say_text("I'm not moving this time").wait_for_completed()

    async def voiceMove(self):
        await cozmo.run_program(self.voiceMoveHW)

    async def trainCozmo(self,robot:cozmo.robot.Robot):
        await robot.say_text("I'm going to be trained now ").wait_for_completed()
        self.makeThread()
        for i in range (1):
            if "Cosmo".lower() in self.voice.speech.lower() or "Cozmo" in self.voice.speech.lower():
                print("This is the voice speech " + self.voice.speech)
                if "Move".lower() in self.voice.speech.lower():
                    print("It is doing the voice methods now")
                    dist = await self.findCurrentState(robot)
                    randomAction = randint(0,3)
                    await self.voiceMoveHW(robot,randomAction)
                    maxValue = np.max(self.voice.moveRewards[dist][:])
                    #Updating the Q matrix for the voice + distance orthogonal
                    self.voice.QMove[dist][randomAction] =  (1 - self.rate) * self.Q[dist][randomAction] + (self.rate * round(self.voice.moveRewards[dist][randomAction] + self.gamma * maxValue, 2))
                    print("This is the move Q Matrix " + self.voice.QMove)
                elif "Stop".lower() in self.voice.speech.lower():
                    randomAction = randint(0,1)
                    maxValue = np.max(self.voice.stopRewards)
                    if randomAction == 1:
                        await robot.say_text("Sorry, I am stopping now").wait_for_completed()
                    self.voice.QStop[randomAction] = (1 - self.rate) * self.voice.QStop[randomAction] + (self.rate * round(self.voice.stopRewards[randomAction] + self.gamma * maxValue, 2))
                    print("This is the stop Q Matrix " + str(self.voice.QStop))
            currentState = await self.findCurrentState(robot)
            await self.nextActionHW(currentState, robot)
            self.update(currentState, self.nextActionIndex, 0.8)
            print("This is the basic Q Matrix " + str(self.Q))
            print("This is the facial Q Matrix " + str(self.facialQ))

    async def trainCozmoHW(self):
        await cozmo.run_program(self.trainCozmo)

    def update(self,currentState,action,gamma):
        maxValue = np.max(self.Q[currentState][:])
        self.Q[currentState][action] = (1 - self.rate) * self.Q[currentState][action] + (self.rate * round(self.rewards[currentState][action] + gamma * maxValue, 2))

    async def nextActionHW(self,currentState,robot:cozmo.robot.Robot):
        nextActRand = randint(0, 3)
        facialExp = await self.facialExpressionEstimateHW(robot)
        await self.robotMovement(nextActRand, facialExp, currentState, robot)
        global nextActionIndex
        nextActionIndex = nextActRand

    async def nextAction(self):
        await cozmo.run_program(self.nextActionHW)

    async def robotMovement(self,actionNum,facialExp,currentState,robot:cozmo.robot.Robot):

        assert 0 <= actionNum <= 3
        assert currentState == 0 or currentState == 1

        allExps = ["Unknown", "Happy", "Sad", "Neutral", "Surprised", "Angry"]
        facial = False

        for i in range(allExps.__len__()):
            if facialExp.lower() == allExps[i].lower():
                facial = True
        assert facial == True

        if (currentState == 0 and facialExp == "happy"):
            print("staying far")
            await cozmo.run_program(self.robotSayTextIdle)
            return "staying far"

        elif (currentState == 2 and facialExp == "happy"):
            print("staying close")
            await cozmo.run_program(self.robotSayTextIdle)
            return "staying close"

        elif (actionNum == 0):
            print("Moving backwards")
            await cozmo.run_program(self.robotMoveBack)
            return "moving backwards"

        elif (actionNum == 1):
            print("Moved forward")
            await cozmo.run_program(self.robotMoveBack)
            return "moving forwards"

        elif (actionNum == 2):
            print("Greeted")
            await cozmo.run_program(self.robotGreet)
            return "greeting"

        else:
            print("idle")
            return "idle"


    async def robotSayTextIdle(self,robot:cozmo.robot.Robot):
        await robot.say_text("I'm happy to stay here until you tell me to move").wait_for_completed()

    async def robotMoveBack(self,robot:cozmo.robot.Robot):
        await robot.drive_straight(distance_mm(-100), speed_mmps(50)).wait_for_completed()

    async def robotMoveFront(self,robot:cozmo.robot.Robot):
        await robot.drive_straight(distance_mm(100), speed_mmps(50)).wait_for_completed()

    async def robotGreet(self,robot:cozmo.robot.Robot):
        await robot.say_text("Hello how are you doing today?").wait_for_completed()

    async def facialExpressionEstimateHW(self,robot: cozmo.robot.Robot):

        face = None
        while True:
            if face and face.is_visible:
                robot.enable_facial_expression_estimation(True)
                maxValue = np.max(self.facialQ)
                self.facialQ[0] = (1 - self.rate) * self.facialQ[0] + (self.rate * round(self.facialRewards[0] + self.gamma * maxValue, 2))
                return face.expression
            else:
                try:
                    await robot.say_text("Sorry, give me 10 seconds to analyse the situation").wait_for_completed()
                    face = await robot.world.wait_for_observed_face(timeout=10)
                except asyncio.TimeoutError:
                    maxValue = np.max(self.facialQ)
                    self.facialQ[1] = (1 - self.rate) * self.facialQ[1] + (self.rate * round(self.facialRewards[1] + self.gamma * maxValue, 2))
                    await robot.say_text("Sorry it will have to be next time").wait_for_completed()
                    print("Didn't find a face.")
                    return

    async def facialExpressionEstimate(self):
        await cozmo.run_program(self.facialExpressionEstimate)

    async def findCurrentState(self, robot: cozmo.robot.Robot):
        await self.moveRobotHead(robot)
        face = await self.searchForFaceHW(robot)
        return face

    async def findCurrentStateHelper(self):
        cozmo.run_program()

    async def moveRobotHead(self,robot: cozmo.robot.Robot):
        robot.move_lift(-3)
        print("Lift Moved")
        await robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
        print("Head Moved")



    async def robotMovingHeadHW(self,robot:cozmo.robot.Robot):
        self.robotHeadPositionBef = robot.head_angle
        self.robotLiftPositionBef = robot.lift_position.height.distance_mm

        if robot.lift_position != cozmo.robot.MIN_LIFT_HEIGHT:
            self.robotLiftPosition = cozmo.robot.MIN_LIFT_HEIGHT.distance_mm
            robot.move_lift(-3)
        if robot.head_angle!=cozmo.robot.MAX_HEAD_ANGLE:
            self.robotHeadPosition = cozmo.robot.MAX_HEAD_ANGLE
            await robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()

    async def robotMovingHead(self):
        await cozmo.run_program(self.robotMovingHeadHW)

    async def hwSearchFace(self,robot:cozmo.robot.Robot):
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

    async def searchForFace(self):
        await cozmo.run_program(self.hwSearchFace)




import cozmo
import asyncio
from cozmo.util import distance_mm, speed_mmps
from random import randint
import numpy as np
import time
import abc
import threading
from threading import Thread
import ctypes
from microIntegration import voiceIntegration

class QLearnSuperClass(abc.ABC):

    nextActionIndex = 0

    def __init__(self):
        self.initState = 0
        self.gamma = 0.8
        self.nextActIndex = 0
        self.Q = []
        self.states = []
        self.rewards = []
        self.rate = 0.3
        self.voice = voiceIntegration()

    @abc.abstractmethod
    def robotMovement(self,*args,**kwargs):
        pass

    @abc.abstractmethod
    async def nextAction(self,*args,**kwargs):
        pass

    def update(self,currentState,action,gamma):
        maxValue = np.max(self.Q[currentState][:])
        self.Q[currentState][action] = (1 - self.rate) * self.Q[currentState][action] + (self.rate * round(self.rewards[currentState][action] + gamma * maxValue, 2))

    @abc.abstractmethod
    def findCurrentState(self,robot:cozmo.robot.Robot):
        pass

    @abc.abstractmethod
    def trainCozmo(self,*args,**kwargs):
        pass

    @abc.abstractmethod
    def testCozmo(self,*args,**kwargs):
        pass

    def startLoop(self,loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeThread(self):
        newLoop = asyncio.new_event_loop()
        t = Thread(target=self.startLoop, args=(newLoop,), daemon=True)
        t.start()
        newLoop.call_soon_threadsafe(self.voice.voiceComms)
        return t

    async def voiceMove(self,robot:cozmo.robot.Robot,action):
            await robot.say_text("I'm going to be acting based on your preferences now").wait_for_completed()
            if action == 0:
                await robot.drive_straight(distance_mm(-150), speed_mmps(50)).wait_for_completed()
            elif action == 2:
                await robot.drive_straight(distance_mm(150), speed_mmps(50)).wait_for_completed()
            elif action == 1:
                await robot.say_text("Are you sure you want me to move?").wait_for_completed()
            elif action == 3:
                await robot.say_text("I'm not moving this time").wait_for_completed()

    async def speechCheck(self,robot:cozmo.robot.Robot,voice):
        print("This is the voice speech " + voice.speech)
        if "Move".lower() in voice.speech.lower():
            print("It is doing the voice methods now")
            dist = await self.findCurrentState(robot)
            randomAction = randint(0, 3)
            await self.voiceMove(robot, randomAction)
            maxValue = np.max(voice.moveRewards[dist][:])
            # Updating the Q matrix for the voice + distance orthogonal
            voice.QMove[dist][randomAction] = (1 - self.rate) * self.Q[dist][randomAction] + (
            self.rate * round(voice.moveRewards[dist][randomAction] + self.gamma * maxValue, 2))
            print("This is the move Q Matrix " + voice.QMove)
        elif "Stop".lower() in voice.speech.lower():
            await robot.say_text("Acting basd on your word stop").wait_for_completed()
            randomAction = randint(0, 1)
            maxValue = np.max(voice.stopRewards)
            if randomAction == 1:
                await robot.say_text("Sorry, I am stopping now").wait_for_completed()
            else:
                await robot.say_text("This simulates idle").wait_for_completed()
                voice.QStop[randomAction] = (1 - self.rate) * voice.QStop[randomAction] + (
            self.rate * round(voice.stopRewards[randomAction] + self.gamma * maxValue, 2))
            print("This is the stop Q Matrix " + str(voice.QStop))

    async def speechCheckTest(self,robot:cozmo.robot.Robot,voice):
        print("This is the voice speech " + voice.speech)
        if "Move".lower() in voice.speech.lower():
            dist = await self.findCurrentState(robot)
            self.maxAction = np.where(voice.QMove[dist][:] == np.max(self.Q[dist][:]))
            self.maxAction = np.amax(self.maxAction[0])
            await self.voiceMove(robot, self.maxAction)
            self.totalScore = self.totalScore + voice.QMove[dist][self.maxAction]
        elif "Stop".lower() in voice.speech.lower():
            maxStop = np.amax(voice.QStop)
            if maxStop == 1:
                await robot.say_text("Sorry, I am stopping now").wait_for_completed()
            else:
                await robot.say_text("I don't feel like obeying you").wait_for_completed()
            self.totalScore = self.totalScore + voice.QStop[maxStop]
            print(str(self.totalScore))

###############################################################################################################################################

class QLearnDistOrthogonal(QLearnSuperClass):

    nextActionIndex = 0

    def __init__(self):
        super(QLearnDistOrthogonal,self).__init__()
        self.actions = [0,1,2,3]
        self.rewards = [[-1.1,-2.1,-1.5,-2],[-0.1,-0.1,1.5,0], [-2.1,-0.1,0.5,0]]
        self.Q = [[0 ,0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0]]
        self.facialRewards = [10,-100]
        self.facialQ = [0,0]
        self.states = [0,1,2]
        self.gamma = 0.8
        self.initState = 0
        self.nextActIndex = 0
        #self.voice = voiceIntegration()
        self.loop = asyncio.get_event_loop()
        self.maxAction = 0
        self.totalScore = 0
        self.rate = 0.3
        self.voice.sleepTime = 20
        #self.name = "voice"

    async def nextAction(self,currentState,robot:cozmo.robot.Robot):
        nextActRand = randint(0, 3)
        facialExp = await self.facialExpressionEstimate(robot)
        await self.robotMovement(nextActRand, facialExp, currentState, robot)
        global nextActionIndex
        nextActionIndex = nextActRand

    async def robotMovement(self,actionNum, facialExp, currentState, robot: cozmo.robot.Robot):
        if (currentState == 0 and facialExp == "happy"):
            await robot.say_text("I will stay here until you tell me to move").wait_for_completed()
            return "staying far"
        elif (currentState == 2 and facialExp == "happy"):
            await robot.say_text("I'm so happy you want me here").wait_for_completed()
            return "staying close"
        elif (actionNum == 0):
            print("Moved backwards")
            await robot.say_text("I´m moving back now").wait_for_completed()
            await robot.drive_straight(distance_mm(-150), speed_mmps(50)).wait_for_completed()
            return "moving backwards"
        elif (actionNum == 1):
            print("Moved forward")
            await robot.say_text("I'm moving forward now").wait_for_completed()
            await robot.drive_straight(distance_mm(150), speed_mmps(50)).wait_for_completed()
            return "moving forwards"
        elif (actionNum == 2):
            print("Greeted")
            await robot.say_text("Hello how are you doing today?").wait_for_completed()
            return "greeting"
        else:
            print("idle")
            await robot.say_text("I'm not moving this time").wait_for_completed()
            return "idle"

    async def facialExpressionEstimate(self,robot: cozmo.robot.Robot):

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

    async def moveRobotHead(self,robot: cozmo.robot.Robot):
        robot.move_lift(-3)
        print("Lift Moved")
        await robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
        print("Head Moved")

    async def searchForFace(self,robot: cozmo.robot.Robot):
        face = None
        while True:
            if face and face.is_visible:

                for face in robot.world.visible_faces:

                    if face.pose.position.x < float(350) and face.pose.position.x > float(150):
                        await robot.say_text("I'm currently in the optimal state").wait_for_completed()
                        currentState = 1
                    elif face.pose.position.x > float(350):
                        await robot.say_text("I´m currently in the far state").wait_for_completed()
                        currentState = 0
                    else:
                        await robot.say_text("I'm currently in the close state").wait_for_completed()
                        currentState = 2
                    return currentState
            else:
                try:
                    await robot.say_text("Sorry, I couldn´t find your face, 10 seconds to do it").wait_for_completed()
                    face = await robot.world.wait_for_observed_face(timeout=10)
                except asyncio.TimeoutError:
                    self.facialQ[1] = (1 - self.rate) * self.facialQ[1] + (self.rate * round(self.facialRewards[1] + self.gamma * self.facialQ[1], 2))
                    await robot.say_text("Sorry, it will have to be next time").wait_for_completed()
                    return None

    async def findCurrentState(self,robot:cozmo.robot.Robot):
        await self.moveRobotHead(robot)
        face = await self.searchForFace(robot)
        return face

    async def nextActionMax(self,currentState,robot:cozmo.robot.Robot):
        #THE ACTION THAT IS CARRIED OUT HAS TO BE THE ONE WITH THE HIGHEST SCORE IN THAT SPECIFIC STATE
        self.maxAction = np.where(self.Q[currentState][:] == np.max(self.Q[currentState][:]))
        print(self.Q[currentState][:])
        print(self.maxAction)
        self.maxAction = np.amax(self.maxAction[0])
        facialExp = await self.facialExpressionEstimate(robot)
        await self.robotMovement(self.maxAction,facialExp,currentState,robot)
        return self.maxAction


    async def trainCozmo(self,robot:cozmo.robot.Robot,voice):
        #self.makeThread()
        #thread = super().makeThread()
        # print(thread)
        # print(self.voice)
        await robot.say_text("I'm training my distance perception now").wait_for_completed()
        for i in range(1):
            if "Cosmo".lower() in voice.speech.lower() or "Cozmo".lower() in voice.speech.lower():
                await super().speechCheck(robot,voice)
                voice.speech = ""
            else:
                currentState = await self.findCurrentState(robot)
                if currentState != None:
                    await self.nextAction(currentState, robot)
                    super().update(currentState, nextActionIndex, self.gamma)
                    print("This is the basic Q Matrix " + str(self.Q))
                else:
                    await robot.say_text("Sorry, I didnt find your face, please try putting it in my vision for best results").wait_for_completed()
        time.sleep(10)
        #self.raiseException()

    async def testCozmo(self,robot:cozmo.robot.Robot,voice):
        #await robot.say_text("I'm going to be tested now").wait_for_completed()
        print(self.voice.speech)
        for i in range (1):
            if "Cosmo".lower() in voice.speech.lower() or "Cozmo".lower() in voice.speech.lower():
                await super().speechCheckTest(robot,voice)
                voice.speech = ""
            else:
                currentState = await self.findCurrentState(robot)
                if currentState != None:
                    await self.nextActionMax(currentState, robot)
                    self.totalScore = self.totalScore + self.Q[currentState][self.maxAction]
                    print("This is the basic Q Matrix " + str(self.Q))
                    print(str(self.totalScore))
                else:
                    await robot.say_text("Sorry, I didnt find your face, please try putting it in my vision for best results").wait_for_completed()


#######################################################################################################################333

class QLearnLiftOrthogonal(QLearnSuperClass):

    nextActionIndex = 0

    def __init__(self):
        super(QLearnLiftOrthogonal, self).__init__()
        # 0 = aggressive, 1 = say nicely, 2 = greet, 3 = idle
        self.actions = [0, 1, 2, 3]
        # 0 is far, 1 is optimal, 2 is far, 3 is in air
        self.states = [0,1,2,3]
        self.rewards = [[-0.5, 1, -2, -2], [-0.5, 1, 5, 2],[-0.5, 1, -2,-5],[-1.5, 2,-5, -1, 1]]
        self.Q = [[0, 0, 0, 0], [0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0]]
        self.gamma = 0
        self.initState = 0
        self.nextActIndex = 0
        self.maxAction = 0
        self.totalScore = 0
        self.rate = 0.3
        self.voice = voiceIntegration()
        self.dist = QLearnDistOrthogonal()
        #self.voice = self.dist.voice
        self.voice.sleepTime = 12

    async def findCurrentState(self,robot:cozmo.robot.Robot):
        if robot.is_picked_up:
            currentState = 3
        else:
            x = await self.dist.findCurrentState(robot)
            if x == 0:
                currentState = 0
            elif x == 1:
                currentState = 1
            elif x== 2:
                currentState = 2
            else:
                currentState = None
        return currentState

    async def robotMovement(self,actionNum,robot:cozmo.robot.Robot):
        if actionNum == 0:
            await robot.play_anim("anim_reacttocliff_pickup_01").wait_for_completed()
        elif actionNum == 1:
            await robot.say_text("I like to be on the table, don´t pick me").wait_for_completed()
        elif actionNum == 2:
            await robot.say_text("Hello how are you doing today").wait_for_completed()
        else:
            await robot.say_text("I'm not doing anything").wait_for_completed()

    async def nextAction(self,robot:cozmo.robot.Robot):
        nextActRand = randint(0,len(self.actions)-1)
        await self.robotMovement(nextActRand,robot)
        global nextActionIndex
        nextActionIndex = nextActRand

    def startLoop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeThread(self):
        newLoop = asyncio.new_event_loop()
        t = Thread(target=self.startLoop, args=(newLoop,), daemon=True)
        t.start()
        newLoop.call_soon_threadsafe(self.voice.voiceComms)
        return t

    async def currentStateEvaluation(self,robot:cozmo.robot.Robot):
        currentState = await self.findCurrentState(robot)
        if currentState != None:
            await self.nextAction(robot)
            super().update(currentState, nextActionIndex, self.gamma)
            print("This is the basic Q Matrix " + str(self.Q))
        else:
            await robot.say_text("Sorry, I didnt find your face, please try putting it in my vision for best results").wait_for_completed()
        time.sleep(2)

    async def currentStateEvaluationTest(self,robot:cozmo.robot.Robot):
        currentState = await self.findCurrentState(robot)
        if currentState != None:
            await self.nextActionMax(currentState,robot)
            self.totalScore = self.totalScore + self.Q[currentState][self.maxAction]
            print(str(self.totalScore))
            print("This is the basic Q Matrix " + str(self.Q))
        else:
            await robot.say_text("Sorry, I didnt find your face, please try putting it in my vision for best results").wait_for_completed()
        time.sleep(2)

    async def trainCozmo(self, robot: cozmo.robot.Robot,voice):
        #super().makeThread()
        #await robot.say_text("I'm learning how to act when i'm lifted").wait_for_completed()
        for i in range (1):
            if "Cosmo".lower() in voice.speech.lower() or "Cozmo".lower() in voice.speech.lower():
                print("THIS IS TO CHECK THE CARRIED ON SPEECH")
                print(voice.speech)
                await super().speechCheck(robot,voice)
            else:
                await self.currentStateEvaluation(robot)
        #self.raiseException()

    async def nextActionMax(self,currentState,robot:cozmo.robot.Robot):
        self.maxAction = np.where(self.Q[currentState][:] == np.max(self.Q[currentState][:]))
        self.maxAction = np.amax(self.maxAction[0])
        await self.robotMovement(self.maxAction,robot)
        return self.maxAction

    async def testCozmo(self,robot:cozmo.robot.Robot,voice):
        #self.makeThread()
        #await robot.say_text("I'm going to be tested now").wait_for_completed()
        for i in range (1):
            if "Cosmo".lower() in voice.speech.lower() or "Cozmo".lower() in voice.speech.lower():
                await super().speechCheckTest(robot,voice)
                voice.speech = ""
            else:
                await self.currentStateEvaluationTest(robot)

####################################################################################################################

class QLearnTurnOrthogonal(QLearnSuperClass):

    nextActionIndex = 0

    def __init__(self):
        super(QLearnTurnOrthogonal, self).__init__()
        self.actions = [0, 1, 2]
        self.rewards = [[-0.5, 1, -2, -2], [-0.5, 1, 5, 2],[-0.5, 1, -2, -3], [1.5, -2, -1, 1]]
        self.Q = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.states = [0, 1, 2, 3]
        self.gamma = 0
        self.initState = 0
        self.nextActIndex = 0
        self.voice = voiceIntegration()
        self.dist = QLearnDistOrthogonal()
        self.lift = QLearnLiftOrthogonal()
        self.maxAction = 0
        self.voice.sleepTime = 12
        self.totalScore = 0
        self.rate = 0.3
        self.name = "voice"

    def startLoop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeThread(self):
        newLoop = asyncio.new_event_loop()
        t = Thread(target=self.startLoop, args=(newLoop,), daemon=True)
        t.start()
        newLoop.call_soon_threadsafe(self.voice.voiceComms)
        return t

    async def findCurrentState(self,robot:cozmo.robot.Robot):
        angle = str(robot.pose_pitch.degrees)
        if 90 < float(angle) < 180:
            await robot.say_text("I am currently upside down").wait_for_completed()
            currentState = 3
        else:
            x = await self.dist.findCurrentState(robot)
            if x == 0:
                currentState = 0
            elif x == 1:
                currentState = 1
            else:
                currentState = 2
        return currentState


    async def robotMovement(self,actionNum,robot:cozmo.robot.Robot):
        if(actionNum==1):
            await robot.say_text("Why are you turning me around you idiot").wait_for_completed()
            print("THIS IS THE TURNED AROUND ORTHOGONAL")
            await robot.play_anim("anim_reacttocliff_faceplantroll_02").wait_for_completed()
            time.sleep(2)
        elif actionNum == 0:
            print("THIS IS THE TURNED AROUND ORTHOGONAL")
            await robot.say_text("I don´t like to be flipped, please rotate me around again").wait_for_completed()
        else:
            await robot.say_text("Hello, how are you doing today").wait_for_completed()

    async def nextAction(self,robot:cozmo.robot.Robot):
        self.lift.nextAction(robot)

    async def nextActionMax(self,currentState, robot:cozmo.robot.Robot):
        self.lift.nextActionMax(currentState, robot)

    async def trainCozmo(self,robot: cozmo.robot.Robot):
        #self.makeThread()
        #await robot.say_text("I'm learning how to act when i'm turned").wait_for_completed()
        for i in range (3):
            await super().speechCheck(robot)
            await self.lift.currentStateEvaluation(robot)
        #self.raiseException()

    async def testCozmo(self,robot:cozmo.robot.Robot):
        #await robot.say_text("I'm testing how to act when i'm turned").wait_for_completed()
        for i in range (1):
            await super().speechCheckTest(robot)
            await self.lift.currentStateEvaluationTest(robot)



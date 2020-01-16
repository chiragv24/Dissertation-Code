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

##################################################################################

class QLearnDistOrthogonal(QLearnSuperClass):

    nextActionIndex = 0

    def __init__(self):
        super(QLearnDistOrthogonal,self).__init__()
        self.actions = [0,1,2,3]
        self.rewards = [[-1.1,-2.1,-1.5,-2],[-0.1,-0.1,1.5,0], [-2.1,-0.1,0.5,0]]
        self.Q = [[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        self.states = [0,1,2]
        self.gamma = 0.8
        self.initState = 0
        self.nextActIndex = 0
        self.voice = voiceIntegration()
        self.loop = asyncio.get_event_loop()

    def startLoop(self,loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeThread(self):
        newLoop = asyncio.new_event_loop()
        t = Thread(target=self.startLoop, args=(newLoop,), daemon=True)
        t.start()
        newLoop.call_soon_threadsafe(self.voice.voiceComms)

    async def voiceMove(self,robot:cozmo.robot.Robot,dist):
            if dist == 0:
                await robot.drive_straight(distance_mm(-150), speed_mmps(50)).wait_for_completed()
            elif dist == 2:
                await robot.drive_straight(distance_mm(150), speed_mmps(50)).wait_for_completed()
            elif dist == 1:
                await robot.say_text("I'm in the best state though").wait_for_completed()


    async def trainCozmo(self,robot:cozmo.robot.Robot):
        self.makeThread()
        for i in range (5):
            if "Cosmo".lower() in self.voice.speech.lower() or "Cozmo" in self.voice.speech.lower():
                print("This is the voice speech " + self.voice.speech)
                if "Move".lower() in self.voice.speech.lower():
                    dist = await self.findCurrentState(robot)
                    await self.voiceMove(robot,dist)
                elif "Stop".lower() in self.voice.speech.lower():
                    await robot.say_text("Sorry, I am stopping now").wait_for_completed()
                break
            else:
                currentState = await self.findCurrentState(robot)
                await self.nextAction(currentState, robot)
                self.update(currentState, nextActionIndex, 0.8)
                print(self.Q)

    def update(self,currentState,action,gamma):
        self.Q[currentState][action] = self.Q[currentState][action] + round(self.rewards[currentState][action] + gamma * np.max(self.rewards[currentState][:]), 2)

    async def nextAction(self,currentState,robot:cozmo.robot.Robot):
        nextActRand = randint(0, 3)
        facialExp = await self.facialExpressionEstimate(robot)
        await self.robotMovement(nextActRand, facialExp, currentState, robot)
        # THIS CAN BE A PROBLEM
        global nextActionIndex
        nextActionIndex = nextActRand

    async def robotMovement(self,actionNum, facialExp, currentState, robot: cozmo.robot.Robot):
        if (currentState == 0 and facialExp == "happy"):
            await robot.say_text("I will stay here until you tell me to move").wait_for_completed()
        elif (currentState == 2 and facialExp == "happy"):
            print("Moved backwards")
            print(robot)
            await robot.say_text("I'm so happy you want me here").wait_for_completed()
        elif (actionNum == 0):
            print("Moved backwards")
            await robot.say_text("I´m moving back now").wait_for_completed()
            await robot.drive_straight(distance_mm(-150), speed_mmps(50)).wait_for_completed()
        elif (actionNum == 1):
            print("Moved forward")
            await robot.say_text("I'm moving forward now").wait_for_completed()
            await robot.drive_straight(distance_mm(150), speed_mmps(50)).wait_for_completed()
        elif (actionNum == 2):
            print("Greeted")
            await robot.say_text("Hello how are you doing today?").wait_for_completed()
        else:
            print("idle")
            await robot.say_text("I'm not moving this time").wait_for_completed()

    async def facialExpressionEstimate(self,robot: cozmo.robot.Robot):
        face = None
        while True:
            if face and face.is_visible:
                robot.enable_facial_expression_estimation(True)
                return face.expression
            else:
                try:
                    await robot.say_text("Sorry, give me 10 seconds to analyse the situation").wait_for_completed()
                    face = await robot.world.wait_for_observed_face(timeout=10)
                except asyncio.TimeoutError:
                    await robot.say_text("Sorry it will have to be next time").wait_for_completed()
                    print("Didn't find a face.")
                    return

    async def findCurrentState(self,robot:cozmo.robot.Robot):
        await self.moveRobotHead(robot)
        face = await self.searchForFace(robot)
        return face

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
                    await robot.say_text("Sorry, it will have to be next time").wait_for_completed()
                    return


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
        self.voice = voiceIntegration()
        self.dist = QLearnDistOrthogonal()

    def randomState(self):
        randomAction = randint(0,1)
        if randomAction == 1:
            self.greeted = False
        else:
            self.greeted = True

    async def findCurrentState(self,robot:cozmo.robot.Robot):
        ##Greeted is state 0 and not greeted is state 1
        self.randomState()
        if self.greeted == False:
            currentState = 1
        else:
            currentState = 0
        return currentState

    async def robotMovement(self,actionNum,robot:cozmo.robot.Robot):
        if(actionNum==1):
            print("THIS IS THE GREET ORTHOGONAL")
            await robot.say_text("Hello how are you doing today?, I´m Cozmo").wait_for_completed()
            self.greeted = True
        else:
            print("THIS IS THE GREET AROUND ORTHOGONAL")
            await robot.say_text("Hello again, I´m Cozmo").wait_for_completed()

    async def nextAction(self,robot:cozmo.robot.Robot):
        nextActRand = randint(0,1)
        await self.robotMovement(nextActRand,robot)
        global nextActionIndex
        nextActionIndex = nextActRand

    def update(self,currentState,action,gamma):
        self.Q[currentState][action] =  self.Q[currentState][action] + round(self.rewards[currentState][action] + gamma * np.max(self.rewards[currentState][:]), 2)

    def startLoop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeThread(self):
        newLoop = asyncio.new_event_loop()
        t = Thread(target=self.startLoop, args=(newLoop,), daemon=True)
        t.start()
        newLoop.call_soon_threadsafe(self.voice.voiceComms)

    async def trainCozmo(self, robot: cozmo.robot.Robot):
        self.makeThread()
        for i in range(5):
            if "Cosmo".lower() in self.voice.speech.lower() or "Cozmo" in self.voice.speech.lower():
                if "Move".lower() in self.voice.speech.lower():
                    dist = await self.dist.findCurrentState(robot)
                    await self.dist.voiceMove(robot,dist)
                elif "Stop".lower() in self.voice.speech.lower():
                    await robot.say_text("Sorry, I am stopping now").wait_for_completed()
                break
            else:
                currentState = await self.findCurrentState(robot)
                await self.nextAction(robot)
                self.update(currentState, nextActionIndex, 0.8)
                print(self.Q)
                time.sleep(5)

###############THIRD ORTHOGONAL #################################################

class QLearnLiftOrthogonal(QLearnSuperClass):

    nextActionIndex = 0

    def __init__(self):
        super(QLearnLiftOrthogonal, self).__init__()
        self.actions = [0, 1]
        self.rewards = [[-0.5, 1], [-1.5, 2]]
        self.Q = [[0, 0], [0, 0]]
        self.states = [0, 1]
        self.gamma = 0
        self.initState = 0
        self.nextActIndex = 0
        self.voice = voiceIntegration()
        self.dist = QLearnDistOrthogonal()

    def findCurrentState(self,robot:cozmo.robot.Robot):
        if robot.is_picked_up:
            currentState = 1
        else:
            currentState = 0
        return currentState

    async def robotMovement(self,actionNum,robot:cozmo.robot.Robot):
        if actionNum == 0:
            await robot.play_anim("anim_reacttocliff_pickup_01").wait_for_completed()
            print("Picked up ")
        else:
            await robot.say_text("I like to be on the table, don´t pick me").wait_for_completed()
            print("On table")

    async def nextAction(self,robot:cozmo.robot.Robot):
        nextActRand = randint(0,1)
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

    async def trainCozmo(self, robot: cozmo.robot.Robot):
        self.makeThread()
        for i in range (15):
            if "Cosmo".lower() in self.voice.speech.lower() or "Cozmo" in self.voice.speech.lower():
                if "Move".lower() in self.voice.speech.lower():
                    dist = await self.dist.findCurrentState(robot)
                    await self.dist.voiceMove(robot,dist)
                elif "Stop".lower() in self.voice.speech.lower():
                    await robot.say_text("Sorry, I am stopping now").wait_for_completed()
                break
            else:
                currentState = self.findCurrentState(robot)
                await self.nextAction(robot)
                self.update(currentState, nextActionIndex, 0.8)
                print(self.Q)
                #time.sleep(5)

    def update(self,currentState,action,gamma):
        print(self.rewards[currentState][:])
        self.Q[currentState][action] = self.Q[currentState][action] + round(self.rewards[currentState][action] + gamma * np.max(self.rewards[currentState][:]), 2)

###############FOURTH ORTHOGONAL ########################################################

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
        self.nextActIndex = 0
        self.voice = voiceIntegration()
        self.dist = QLearnDistOrthogonal()
        self.greet = QLearnGreetOrthogonal()

    async def findCurrentState(self,robot:cozmo.robot.Robot):
        robot.enable_all_reaction_triggers(True)
        angle = str(robot.pose_pitch.degrees)
        if 90 < float(angle) < 180:
            currentState = 1
        else:
            currentState = 0
        return currentState

    async def robotMovement(self,actionNum,robot:cozmo.robot.Robot):
        if(actionNum==1):
            print("THIS IS THE TURNED AROUND ORTHOGONAL")
            await robot.play_anim("anim_reacttocliff_faceplantroll_02").wait_for_completed()
            time.sleep(5)
        else:
            print("THIS IS THE TURNED AROUND ORTHOGONAL")
            await robot.say_text("I don´t like to be flipped, please rotate me around again").wait_for_completed()

    async def nextAction(self,robot:cozmo.robot.Robot):
        nextActRand = randint(0,1)
        await self.robotMovement(nextActRand,robot)
        global nextActionIndex
        nextActionIndex = nextActRand

    def update(self,currentState,action,gamma):
        self.Q[currentState][action] = round(self.rewards[currentState][action] + gamma * np.max(self.rewards[currentState][:]), 2)

    def startLoop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeThread(self):
        newLoop = asyncio.new_event_loop()
        t = Thread(target=self.startLoop, args=(newLoop,), daemon=True)
        t.start()
        newLoop.call_soon_threadsafe(self.voice.voiceComms)

    async def trainCozmo(self,robot: cozmo.robot.Robot):
        self.makeThread()
        for i in range (5):
            if "Cosmo".lower() in self.voice.speech.lower() or "Cozmo" in self.voice.speech.lower():
                if "Move".lower() in self.voice.speech.lower():
                    dist = await self.dist.findCurrentState(robot)
                    await self.dist.voiceMove(robot,dist)
                elif "Stop".lower() in self.voice.speech.lower():
                    await robot.say_text("Sorry, I am stopping now").wait_for_completed()
                break
            else:
                currentState = await self.findCurrentState(robot)
                await self.nextAction(robot)
                self.update(currentState, nextActionIndex, 0.8)
                print(self.Q)
                time.sleep(5)



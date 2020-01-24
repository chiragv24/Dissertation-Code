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
        self.facialRewards = [10,-100]
        self.facialQ = [0,0]
        self.states = [0,1,2]
        self.gamma = 0.8
        self.initState = 0
        self.nextActIndex = 0
        self.voice = voiceIntegration()
        self.loop = asyncio.get_event_loop()
        self.maxAction = 0
        self.totalScore = 0
        self.rate = 0.3

    def startLoop(self,loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeThread(self):
        newLoop = asyncio.new_event_loop()
        t = Thread(target=self.startLoop, args=(newLoop,), daemon=True)
        t.start()
        newLoop.call_soon_threadsafe(self.voice.voiceComms)

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

    async def trainCozmo(self,robot:cozmo.robot.Robot):
        await robot.say_text("I'm training my distance perception now").wait_for_completed()
        self.makeThread()
        for i in range (5):
            if "Cosmo".lower() in self.voice.speech.lower() or "Cozmo" in self.voice.speech.lower():
                print("This is the voice speech " + self.voice.speech)
                if "Move".lower() in self.voice.speech.lower():
                    print("It is doing the voice methods now")
                    dist = await self.findCurrentState(robot)
                    randomAction = randint(0,3)
                    await self.voiceMove(robot,randomAction)
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
            if currentState != None:
                await self.nextAction(currentState, robot)
                self.update(currentState, nextActionIndex, 0.8)
                print("This is the basic Q Matrix " + str(self.Q))
                print("This is the facial Q Matrix " + str(self.facialQ))
            else:
                await robot.say_text("Sorry, I didnt find your face, please try putting it in my vision for best results").wait_for_completed()

    def update(self,currentState,action,gamma):
        maxValue = np.max(self.Q[currentState][:])
        self.Q[currentState][action] = (1 - self.rate) * self.Q[currentState][action] + (self.rate * round(self.rewards[currentState][action] + gamma * maxValue, 2))

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
                    self.facialQ[1] = (1 - self.rate) * self.facialQ[1] + (self.rate * round(self.facialRewards[1] + self.gamma * self.facialQ[1], 2))
                    await robot.say_text("Sorry, it will have to be next time").wait_for_completed()
                    return

    async def nextActionMax(self,currentState,robot:cozmo.robot.Robot):
        #THE ACTION THAT IS CARRIED OUT HAS TO BE THE ONE WITH THE HIGHEST SCORE IN THAT SPECIFIC STATE
        self.maxAction = np.where(self.Q[currentState][:] == np.max(self.Q[currentState][:]))
        print(self.Q[currentState][:])
        print(self.maxAction)
        self.maxAction = np.amax(self.maxAction[0])
        facialExp = await self.facialExpressionEstimate(robot)
        await self.robotMovement(self.maxAction,facialExp,currentState,robot)
        return self.maxAction

    async def testCozmo(self,robot:cozmo.robot.Robot):
        await robot.say_text("I'm going to be tested now").wait_for_completed()
        self.makeThread()
        for i in range (100):
            if "Cosmo".lower() in self.voice.speech.lower() or "Cozmo" in self.voice.speech.lower():
                print("This is the voice speech " + self.voice.speech)
                if "Move".lower() in self.voice.speech.lower():
                    dist = await self.findCurrentState(robot)
                    self.maxAction = np.where(self.voice.QMove[dist][:] == np.max(self.Q[dist][:]))
                    self.maxAction = np.amax(self.maxAction[0])
                    await self.voiceMove(robot, self.maxAction)
                    self.totalScore = self.totalScore + self.voice.QMove[dist][self.maxAction]
                    #Updating the Q matrix for the voice + distance orthogonal
                elif "Stop".lower() in self.voice.speech.lower():
                    maxStop = np.amax(self.voice.QStop)
                    if maxStop == 1:
                        await robot.say_text("Sorry, I am stopping now").wait_for_completed()
                    else:
                        await robot.say_text("I don't feel like obeying you").wait_for_completed()
                    self.totalScore = self.totalScore + self.voice.QStop[maxStop]
                    print(str(self.totalScore))
            currentState = await self.findCurrentState(robot)
            await self.nextActionMax(currentState,robot)
            self.totalScore = self.totalScore + self.Q[currentState][self.maxAction]
            print(str(self.totalScore))

#########################################################################################################################################

class QLearnGreetOrthogonal(QLearnSuperClass):

    nextActionIndex = 0

    def __init__(self):
        super(QLearnGreetOrthogonal, self).__init__()
        self.actions = [0, 1]
        self.rewards = [[-0.5, 1.5], [-1.5, 1]]
        self.Q = [[0, 0],[0, 0]]
        self.states = [0, 1]
        self.gamma = 0.5
        self.initState = 0
        self.nextActIndex = 0
        self.greeted = None
        self.voice = voiceIntegration()
        self.dist = QLearnDistOrthogonal()
        self.maxAction = 0
        self.totalScore = 0
        self.lastAction = None
        self.rate = 0.3

    def findCurrentState(self,robot:cozmo.robot.Robot):
        ##Greeted is state 0 and not greeted is state 1
        randomAction = randint(0,1)
        if randomAction == 0:
            self.greeted = 0
        else:
            self.greeted = 1
        return randomAction

    async def robotMovement(self,actionNum,robot:cozmo.robot.Robot):
        assert actionNum == 1 or actionNum == 0
        if(actionNum==1):
            print("THIS IS THE GREET ORTHOGONAL")
            await robot.say_text("Hello how are you doing today?, I´m Cozmo").wait_for_completed()
            self.greeted = True
            self.lastAction = "Greeted"
        else:
            print("THIS IS THE GREET AROUND ORTHOGONAL")
            await robot.say_text("I'm sad").wait_for_completed()
            self.lastAction = "Not Greeted"
        return self.lastAction


    async def nextAction(self,robot:cozmo.robot.Robot):
        nextActRand = randint(0,1)
        await self.robotMovement(nextActRand,robot)
        global nextActionIndex
        nextActionIndex = nextActRand

    def update(self,currentState,action,gamma):
        assert currentState == 0 or currentState == 1
        assert action == 0 or action == 1
        assert 0 < gamma <=1
        maxValue = np.max(self.Q[currentState][:])
        self.Q[currentState][action] = (1 - self.rate) * self.Q[currentState][action] + (self.rate * round(self.rewards[currentState][action] + gamma * maxValue, 2))

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
        await robot.say_text("I'm training when to greet").wait_for_completed()
        for i in range(10):
            if "Cosmo".lower() in self.voice.speech.lower() or "Cozmo" in self.voice.speech.lower():
                 if "Move".lower() in self.voice.speech.lower():
                     randomAction = randint(0,3)
                     dist = await self.dist.findCurrentState(robot)
                     await self.dist.voiceMove(robot,randomAction)
                     maxValue = np.max(self.voice.moveRewards[dist][:])
                     # Updating the Q matrix for the voice + distance orthogonal
                     self.voice.QMove[dist][randomAction] = (1 - self.rate) * self.Q[dist][randomAction] + (self.rate * round(self.voice.moveRewards[dist][randomAction] + self.gamma * maxValue, 2))
                     print("This is the move Q Matrix " + self.voice.QMove)
                 elif "Stop".lower() in self.voice.speech.lower():
                     randomAction = randint(0,1)
                     maxValue = np.max(self.voice.stopRewards)
                     if randomAction == 1:
                         await robot.say_text("Sorry, I am stopping now").wait_for_completed()
                     self.voice.QStop[randomAction] = (1 - self.rate) * self.voice.QStop[randomAction] + (self.rate * round(self.voice.stopRewards[randomAction] + self.gamma * maxValue, 2))
            currentState = await self.findCurrentState(robot)
            await self.nextAction(robot)
            self.update(currentState, nextActionIndex, self.gamma)
            print(self.Q)
            time.sleep(3)

    async def nextActionMax(self,currentState,robot:cozmo.robot.Robot):
        assert currentState == 0 or currentState == 1
        print(self.Q)
        ## THE ACTION THAT IS CARRIED OUT HAS TO BE THE ONE WITH THE HIGHEST SCORE IN THAT SPECIFIC STATE
        self.maxAction = np.where(self.Q[currentState][:] == np.max(self.Q[currentState][:]))
        self.maxAction = np.amax(self.maxAction[0])
        await self.robotMovement(self.maxAction,robot)

    async def testCozmo(self,robot:cozmo.robot.Robot):
        await robot.say_text("I'm going to be tested now").wait_for_completed()
        self.makeThread()
        for i in range (100):
            if "Cosmo".lower() in self.voice.speech.lower() or "Cozmo" in self.voice.speech.lower():
                print("This is the voice speech " + self.voice.speech)
                if "Move".lower() in self.voice.speech.lower():
                    dist = await self.findCurrentState(robot)
                    self.maxAction = np.where(self.voice.QMove[dist][:] == np.max(self.Q[dist][:]))
                    self.maxAction = np.amax(self.maxAction[0])
                    await self.dist.voiceMove(robot, self.maxAction)
                    self.totalScore = self.totalScore + self.voice.QMove[dist][self.maxAction]
                    #Updating the Q matrix for the voice + distance orthogonal
                elif "Stop".lower() in self.voice.speech.lower():
                    maxStop = np.amax(self.voice.QStop)
                    if maxStop == 1:
                        await robot.say_text("Sorry, I am stopping now").wait_for_completed()
                    else:
                        await robot.say_text("I don't feel like obeying you").wait_for_completed()
                    self.totalScore = self.totalScore + self.voice.QStop[maxStop]
                    print(str(self.totalScore))
            currentState = await self.findCurrentState(robot)
            await self.nextActionMax(currentState,robot)
            self.totalScore = self.totalScore + self.Q[currentState][self.maxAction]
            print(str(self.totalScore))

###########################################################################################################################

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
        self.maxAction = 0
        self.totalScore = 0
        self.rate = 0.3
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
        await robot.say_text("I'm learning how to act when i'm lifted").wait_for_completed()
        for i in range (50):
            if "Cosmo".lower() in self.voice.speech.lower() or "Cozmo" in self.voice.speech.lower():
                if "Move".lower() in self.voice.speech.lower():
                    randomAction = randint(0, 3)
                    dist = await self.dist.findCurrentState(robot)
                    await self.dist.voiceMove(robot,randomAction)
                    maxValue = np.max(self.voice.moveRewards[dist][:])
                    self.voice.QMove[dist][randomAction] =  (1 - self.rate) * self.Q[dist][randomAction] + (self.rate * round(self.voice.moveRewards[dist][randomAction] + self.gamma * maxValue, 2))
                elif "Stop".lower() in self.voice.speech.lower():
                    randomAction = randint(0,1)
                    maxValue = np.max(self.voice.stopRewards)
                    if randomAction == 1:
                        await robot.say_text("Sorry, I am stopping now").wait_for_completed()
                    self.voice.QStop[randomAction] = (1 - self.rate) * self.voice.QStop[randomAction] + (self.rate * round(self.voice.stopRewards[randomAction] + self.gamma * maxValue, 2))
            currentState = self.findCurrentState(robot)
            await self.nextAction(robot)
            self.update(currentState, nextActionIndex, 0.8)
            print(self.Q)

    def update(self,currentState,action,gamma):
        maxValue = np.max(self.Q[currentState][:])
        self.Q[currentState][action] = (1 - self.rate) * self.Q[currentState][action] + (self.rate * round(self.rewards[currentState][action] + gamma * maxValue, 2))

    async def nextActionMax(self,currentState,robot:cozmo.robot.Robot):
        #THE ACTION THAT IS CARRIED OUT HAS TO BE THE ONE WITH THE HIGHEST SCORE IN THAT SPECIFIC STATE
        self.maxAction = np.where(self.Q[currentState][:] == np.max(self.Q[currentState][:]))
        self.maxAction = np.amax(self.maxAction[0])
        await self.robotMovement(self.maxAction,robot)
        return self.maxAction

    async def testCozmo(self,robot:cozmo.robot.Robot):
        await robot.say_text("I'm going to be tested now").wait_for_completed()
        self.makeThread()
        for i in range (50):
            if "Cosmo".lower() in self.voice.speech.lower() or "Cozmo" in self.voice.speech.lower():
                print("This is the voice speech " + self.voice.speech)
                if "Move".lower() in self.voice.speech.lower():
                    dist = await self.dist.findCurrentState(robot)
                    self.maxAction = np.where(self.voice.QMove[dist][:] == np.max(self.Q[dist][:]))
                    self.maxAction = np.amax(self.maxAction[0])
                    await self.dist.voiceMove(robot, self.maxAction)
                    self.totalScore = self.totalScore + self.voice.QMove[dist][self.maxAction]
                    #Updating the Q matrix for the voice + distance orthogonal
                elif "Stop".lower() in self.voice.speech.lower():
                    maxStop = np.amax(self.voice.QStop)
                    if maxStop == 1:
                        await robot.say_text("Sorry, I am stopping now").wait_for_completed()
                    else:
                        await robot.say_text("I don't feel like obeying you").wait_for_completed()
                    self.totalScore = self.totalScore + self.voice.QStop[maxStop]
                    print(str(self.totalScore))
            currentState = self.findCurrentState(robot)
            await self.nextActionMax(currentState,robot)
            self.totalScore = self.totalScore + self.Q[currentState][self.maxAction]
            print(str(self.totalScore))


#######################################################################################################################

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
        self.maxAction = 0
        self.totalScore = 0
        self.rate = 0.3

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
            await robot.say_text("Why are you turning me around you idiot").wait_for_completed()
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
        maxValue = np.max(self.Q[currentState][:])
        self.Q[currentState][action] = (1 - self.rate) * self.Q[currentState][action] + (self.rate * round(self.rewards[currentState][action] + gamma * maxValue, 2))

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
        await robot.say_text("I'm training how to act when I'm turned around").wait_for_completed()
        for i in range (50):
            if "Cosmo".lower() in self.voice.speech.lower() or "Cozmo" in self.voice.speech.lower():
                if "Move".lower() in self.voice.speech.lower():
                    randomAction = randint(0,3)
                    dist = await self.dist.findCurrentState(robot)
                    maxValue = np.max(self.voice.moveRewards[dist][:])
                    await self.dist.voiceMove(robot,randomAction)
                    self.voice.QMove[dist][randomAction] =  (1 - self.rate) * self.Q[dist][randomAction] + (self.rate * round(self.voice.moveRewards[dist][randomAction] + self.gamma * maxValue, 2))
                elif "Stop".lower() in self.voice.speech.lower():
                    randomAction = randint(0,1)
                    maxValue = np.max(self.voice.stopRewards)
                    if randomAction == 1:
                        await robot.say_text("Sorry, I am stopping now").wait_for_completed()
                    self.voice.QStop[randomAction] = (1 - self.rate) * self.Q[randomAction] + (self.rate * round(self.voice.stopRewards[randomAction] + self.gamma * maxValue, 2))
            currentState = await self.findCurrentState(robot)
            await self.nextAction(robot)
            self.update(currentState, nextActionIndex, 0.8)
            print(self.Q)
            time.sleep(1)

    async def nextActionMax(self,currentState,robot:cozmo.robot.Robot):
        #THE ACTION THAT IS CARRIED OUT HAS TO BE THE ONE WITH THE HIGHEST SCORE IN THAT SPECIFIC STATE
        self.maxAction = np.where(self.Q[currentState][:] == np.max(self.Q[currentState][:]))
        self.maxAction = np.amax(self.maxAction[0])
        await self.robotMovement(self.maxAction,robot)

    async def testCozmo(self,robot:cozmo.robot.Robot):
        await robot.say_text("I'm going to be tested now").wait_for_completed()
        self.makeThread()
        for i in range (100):
            if "Cosmo".lower() in self.voice.speech.lower() or "Cozmo" in self.voice.speech.lower():
                print("This is the voice speech " + self.voice.speech)
                if "Move".lower() in self.voice.speech.lower():
                    dist = await self.dist.findCurrentState(robot)
                    self.maxAction = np.where(self.voice.QMove[dist][:] == np.max(self.Q[dist][:]))
                    self.maxAction = np.amax(self.maxAction[0])
                    await self.dist.voiceMove(robot, self.maxAction)
                    self.totalScore = self.totalScore + self.voice.QMove[dist][self.maxAction]
                    #Updating the Q matrix for the voice + distance orthogonal
                elif "Stop".lower() in self.voice.speech.lower():
                    maxStop = np.amax(self.voice.QStop)
                    if maxStop == 1:
                        await robot.say_text("Sorry, I am stopping now").wait_for_completed()
                    else:
                        await robot.say_text("I don't feel like obeying you").wait_for_completed()
                    self.totalScore = self.totalScore + self.voice.QStop[maxStop]
                    print(str(self.totalScore))
            currentState = await self.findCurrentState(robot)
            await self.nextActionMax(currentState,robot)
            self.totalScore = self.totalScore + self.Q[currentState][self.maxAction]
            print(str(self.totalScore))

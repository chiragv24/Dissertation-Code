import cozmo
import asyncio
from cozmo.util import distance_mm, speed_mmps, degrees
from random import randint
import numpy as np
import time
import abc
import threading
import csv
from threading import Thread
import ctypes
from microIntegrationInteractive import voiceIntegration



class QLearnSuperClass(abc.ABC):

    nextActionIndex = 0

    def __init__(self):
        self.initState = 0
        self.gamma = 0.8
        self.nextActIndex = 0
        self.Q = []
        self.states = []
        self.rewards = [1,0,-1]
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
        rating = 0
        self.Q[currentState][action] = (1 - self.rate) * self.Q[currentState][action] + (self.rate * round(self.rewards[rating] + gamma * maxValue, 2))

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

    async def speechCheck(self,robot:cozmo.robot.Robot,voice,backVoice):
        print("This is the voice speech " + backVoice.speech)
        if "Move".lower() in backVoice.speech.lower():
            await robot.say_text("Acting based on the word move").wait_for_completed()
            print("It is doing the voice methods now")
            dist = await self.findCurrentState(robot)
            randomAction = randint(0, 3)
            await self.voiceMove(robot, randomAction)
            maxValue = np.max(voice.QMove[dist][:])
            # Updating the Q matrix for the voice + distance orthogonal
            await robot.say_text("What did you think?").wait_for_completed()
            await voice.voiceComms()
            if "good" in voice.speech.lower():
                await robot.say_text("Perfect").wait_for_completed()
                voice.QMove[dist][randomAction] = round((1-self.rate) * voice.QMove[dist][randomAction] + (self.rate * 3 + self.gamma * maxValue),2)
            elif "medium" in voice.speech.lower():
                voice.QMove[dist][randomAction] = round((1-self.rate) * voice.QMove[dist][randomAction] + (self.rate + self.gamma * maxValue),2)
                await robot.say_text("Noted").wait_for_completed()
            elif "bad" in voice.speech.lower():
                await robot.say_text("Has to be improved").wait_for_completed()
                voice.QMove[dist][randomAction] = round((1-self.rate) * voice.QMove[dist][randomAction] + (self.rate * -3 + self.gamma * maxValue),2)
            print("This is the move Q Matrix " + str(voice.QMove))
        elif "Stop".lower() in voice.speech.lower():
            await robot.say_text("Acting based on your word stop").wait_for_completed()
            randomAction = randint(0, 1)
            maxValue = np.max(voice.stopRewards)
            if randomAction == 1:
                await robot.say_text("Sorry, I am stopping now").wait_for_completed()
            else:
                await robot.say_text("I'm not moving thsi time").wait_for_completed()
            await robot.say_text("What did you think?").wait_for_completed()
            await voice.voiceComms()
            if "good" in voice.speech.lower():
                await robot.say_text("Perfect").wait_for_completed()
                voice.QStop[randomAction] = round((1-self.rate) * voice.QStop[randomAction] + (self.rate * 3 + self.gamma * maxValue),2)
            elif "medium" in voice.speech.lower():
                await robot.say_text("Noted").wait_for_completed()
                voice.QStop[randomAction] = round((1-self.rate) * voice.QStop[randomAction] + (self.rate + self.gamma * maxValue),2)
            elif "bad" in voice.speech.lower():
                await robot.say_text("Has to be improved").wait_for_completed()
                voice.QStop[randomAction] = round((1-self.rate) * voice.QStop[randomAction] + (self.rate * -3 + self.gamma * maxValue),2)
            print("This is the stop Q Matrix " + str(voice.QStop))

    async def speechCheckTest(self,robot:cozmo.robot.Robot,voice):
        print("This is the voice speech " + voice.speech)
        if "Move".lower() in voice.speech.lower():
            dist = await self.findCurrentState(robot)
            self.maxAction = np.where(voice.QMove[dist][:] == np.max(self.Q[dist][:]))
            print(self.maxAction)
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
        self.Q = [[0 ,0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0]]
        self.states = [0,1,2]
        self.gamma = 0.8
        self.initState = 0
        self.nextActIndex = 0
        self.voice = voiceIntegration()
        self.loop = asyncio.get_event_loop()
        self.maxAction = 0
        self.totalScore = 0
        self.rate = 0.3
        self.voice.sleepTime = 20

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
            await robot.drive_straight(distance_mm(-350), speed_mmps(75)).wait_for_completed()
            return "moving backwards"
        elif (actionNum == 1):
            print("Moved forward")
            await robot.say_text("I'm moving forward now").wait_for_completed()
            await robot.drive_straight(distance_mm(350), speed_mmps(75)).wait_for_completed()
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
                await robot.say_text("Facial expression analysed, as " + str(face.expression)).wait_for_completed()
                return face.expression
            else:
                try:
                    face = await robot.world.wait_for_observed_face(timeout=10)
                except asyncio.TimeoutError:
                    await robot.say_text("Sorry I couldn't estimate your expression").wait_for_completed()
                    print("Didn't find a face.")
                    return

    async def moveRobotHead(self,robot: cozmo.robot.Robot):
        robot.move_lift(-3)
        await robot.set_head_angle(degrees(25)).wait_for_completed()
        # time.sleep(5)
        # await robot.set_head_angle(cozmo.robot.MAX_HEAD_ANGLE).wait_for_completed()
        # time.sleep(5)
        # robot.drive_straight(distance_mm(-100),speed_mmps(50)).wait_for_completed()

    async def searchForFace(self,robot: cozmo.robot.Robot):
        face = None
        while True:
            if face and face.is_visible:
                for face in robot.world.visible_faces:
                    dist = abs(face.pose.position.x - robot.pose.position.x)
                    if dist < float(850) and dist > float(250):
                        await robot.say_text("I'm currently in the optimal state").wait_for_completed()
                        print("This is the distance from the face " + str(dist))
                        currentState = 1
                    elif dist > float(850):
                        await robot.say_text("I´m currently in the far state").wait_for_completed()
                        print("This is the distance from the face " + str(dist))
                        currentState = 0
                    else:
                        await robot.say_text("I'm currently in the close state").wait_for_completed()
                        print("This is the distance from the face " + str(dist))
                        currentState = 2
                    return currentState
            else:
                try:
                    face = await robot.world.wait_for_observed_face(timeout=10)
                except asyncio.TimeoutError:
                    await robot.say_text("Sorry, it will have to be next time").wait_for_completed()
                    cubeDist = await self.findTheCube(robot)
                    if cubeDist!=None:
                        currentState = None
                        if cubeDist < 250:
                            currentState = 2
                            await robot.say_text("I'm currently in the close state").wait_for_completed()
                        elif cubeDist > 900:
                            currentState = 0
                            await robot.say_text("I'm currently in the far state").wait_for_completed()
                        else:
                            currentState = 1
                            await robot.say_text("I'm currently in the optimal state").wait_for_completed()
                        return currentState
                    else:
                        return None

    async def findCurrentState(self,robot:cozmo.robot.Robot):
        await self.moveRobotHead(robot)
        face = await self.searchForFace(robot)
        return face

    async def nextActionMax(self,currentState,robot:cozmo.robot.Robot):
        #THE ACTION THAT IS CARRIED OUT HAS TO BE THE ONE WITH THE HIGHEST SCORE IN THAT SPECIFIC STATE
        self.maxAction = np.where(self.Q[currentState][:] == np.max(self.Q[currentState][:]))
        self.maxAction = np.amax(self.maxAction[0])
        facialExp = await self.facialExpressionEstimate(robot)
        await self.robotMovement(self.maxAction,facialExp,currentState,robot)
        return self.maxAction

    def writeToFile(self,currentState,action,reward):
        file = open('trainData.txt',mode='a')
        file.write(str(currentState) + " " + str(action) + " " + str(reward))
        file.write("\n")
        file.close()

    async def findTheCube(self,robot:cozmo.robot.Robot):
        await robot.set_head_angle(degrees(-15)).wait_for_completed()
        await robot.say_text("I'm trying to  find the cube now").wait_for_completed()
        try:
            cube = await robot.world.wait_for_observed_light_cube(timeout=30)
            x = cube.pose.position.x
            dist = abs(robot.pose.position.x - x)
        except asyncio.TimeoutError:
            await robot.say_text("Sorry I didn't find the cube either").wait_for_completed()
            dist = None
        print(dist)
        return dist


    async def trainCozmo(self,robot:cozmo.robot.Robot,voice,backVoice):
        open('trainData.txt',mode='w')
        await robot.say_text("I'm training my distance perception now").wait_for_completed()
        for i in range (100):
            if "Move".lower() in backVoice.speech.lower() or "Stop".lower() in backVoice.speech.lower():
                if "Cosmo" in backVoice.speech.lower() or "Cozmo".lower() in backVoice.speech.lower():
                    await super().speechCheck(robot,voice,backVoice)
                    backVoice.speech = ""
            print("This is train loop " + str(i))
            currentState = await self.findCurrentState(robot)
            if currentState != None:
                maxValue = np.max(self.Q[currentState][:])
                await self.nextAction(currentState, robot)
                await robot.say_text("What did you think?").wait_for_completed()
                try:
                    await asyncio.wait_for(voice.voiceComms(),10)
                    reward = 0
                    print("This is the code words " + voice.speech)
                    if "good".lower() in voice.speech:
                        bef = self.Q[currentState][nextActionIndex]
                        self.Q[currentState][nextActionIndex] = (1 - self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * round(3 + self.gamma * maxValue))
                        reward = self.Q[currentState][nextActionIndex] - bef
                        await robot.say_text("Perfect").wait_for_completed()
                    elif "medium".lower() in voice.speech:
                        bef = self.Q[currentState][nextActionIndex]
                        self.Q[currentState][nextActionIndex] = (1 - self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * round(self.gamma * maxValue))
                        reward = self.Q[currentState][nextActionIndex] - bef
                        await robot.say_text("Noted").wait_for_completed()
                    elif "bad".lower() in voice.speech:
                        bef = self.Q[currentState][nextActionIndex]
                        self.Q[currentState][nextActionIndex] = (1 - self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * round(-3 + self.gamma * maxValue))
                        reward = self.Q[currentState][nextActionIndex] - bef
                        await robot.say_text("Not Good").wait_for_completed()
                    else:
                        await robot.say_text("Sorry I couldn't understand y ou").wait_for_completed()
                    print(str(self.Q))
                    self.writeToFile(currentState,nextActionIndex,reward)
                    print("THIS IS THE LOGGED INFO " + str(currentState) + " " + str(nextActionIndex) + " " + str(self.Q[currentState][nextActionIndex]))
                except asyncio.TimeoutError:
                    robot.say_text("Sorry I didn´t hear anything").wait_for_completed()
            else:
                await robot.say_text("Sorry I couldn't find your face").wait_for_completed()

    async def testCozmo(self,robot:cozmo.robot.Robot,voice):
        await robot.say_text("I'm going to be tested now").wait_for_completed()
        for i in range(1):
            if "Move".lower() in voice.speech.lower() or "Stop".lower() in voice.speech.lower():
                if "Cozmo".lower() in voice.speech.lower() or "Cosmo".lower() in voice.speech.lower():
                    await super().speechCheckTest(robot,voice)
                    voice.speech = ""
            else:
                currentState = await self.findCurrentState(robot)
                if currentState!=None:
                    await self.nextActionMax(currentState,robot)
                    self.totalScore = self.totalScore + self.Q[currentState][self.maxAction]
                else:
                    await robot.say_text("Sorry I couldn´t find your face").wait_for_completed()

################################################################################################################################

class QLearnLiftOrthogonal(QLearnSuperClass):

    def __init__(self):
        super(QLearnLiftOrthogonal,self).__init__()
        self.actions = [0,1,2,3]
        self.Q = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        self.states = [0,1,2,3]
        self.gamma = 0.8
        self.initState = 0
        self.nextActIndex = 0
        self.voice = voiceIntegration()
        self.loop = asyncio.get_event_loop()
        self.maxAction = 0
        self.dist = QLearnDistOrthogonal()
        self.totalScore = 0
        self.rate = 0.3
        self.voice.sleepTime = 20

    async def findCurrentState(self,robot:cozmo.robot.Robot):
        if robot.is_picked_up:
            await robot.say_text("Oh I am lifted now").wait_for_completed()
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

    async def currentStateEvaluation(self,robot:cozmo.robot.Robot,voice):
        currentState = await self.findCurrentState(robot)
        maxValue = np.max(self.Q[currentState][:])
        if currentState != None:
            await self.nextAction(robot)
            await robot.say_text("What did you think?").wait_for_completed()
            await voice.voiceComms()
            print("This is the code words " + voice.speech)
            if "good".lower() in voice.speech:
                self.Q[currentState][nextActionIndex] = (1-self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * round(3 + self.gamma * maxValue))
                await robot.say_text("Perfect").wait_for_completed()
            elif "medium".lower() in voice.speech:
                self.Q[currentState][nextActionIndex] = (1-self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * + round(self.gamma * maxValue))
                await robot.say_text("Noted").wait_for_completed()
            elif "bad".lower() in voice.speech:
                self.Q[currentState][nextActionIndex] = (1-self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * round(-3 + self.gamma * maxValue))
                await robot.say_text("Has to be improved").wait_for_completed()
            else:
                await robot.say_text("Sorry I didn't hear anything").wait_for_completed()
            print(str(self.Q))
            print("This is the basic Q Matrix " + str(self.Q))
        else:
            await robot.say_text("Sorry, I didnt find your face, please try putting it in my vision for best results").wait_for_completed()
        time.sleep(2)

    async def nextActionMax(self, currentState, robot: cozmo.robot.Robot):
        self.maxAction = np.where(self.Q[currentState][:] == np.max(self.Q[currentState][:]))
        self.maxAction = np.amax(self.maxAction[0])
        await self.robotMovement(self.maxAction, robot)
        return self.maxAction

    async def currentStateEvaluationTest(self, robot: cozmo.robot.Robot):
        currentState = await self.findCurrentState(robot)
        if currentState != None:
            await self.nextActionMax(currentState, robot)
            self.totalScore = self.totalScore + self.Q[currentState][self.maxAction]
            print(str(self.totalScore))
            print("This is the basic Q Matrix " + str(self.Q))
        else:
            await robot.say_text("Sorry, I don't know my position").wait_for_completed()
        time.sleep(2)

    async def trainCozmo(self, robot: cozmo.robot.Robot, voice, backVoice):
        await robot.say_text("I'm learning how to act if i'm lifted").wait_for_completed()
        for i in range(10):
            print("This is the train loop counter " + str(i))
            if "Move".lower() in backVoice.speech.lower() or "Stop".lower() in backVoice.speech.lower():
                if "Cosmo".lower() in backVoice.speech.lower() or "Cozmo".lower() in backVoice.speech.lower():
                    print(voice.speech)
                    await super().speechCheck(robot,voice,backVoice)
                    backVoice.speech = ""
            else:
                await self.currentStateEvaluation(robot,voice)

    async def testCozmo(self, robot: cozmo.robot.Robot, voice):
        await robot.say_text("I'm going to be tested now").wait_for_completed()
        for i in range(1):
            if "Move".lower() in voice.speech.lower() or "Stop".lower() in voice.speech.lower() and "Move".lower() in voice.speech.lower() or "Stop".lower() in voice.speech.lower():
                await super().speechCheckTest(robot, voice)
                voice.speech = ""
            else:
                await self.currentStateEvaluationTest(robot)

###################################################################################################################################

class QLearnTurnOrthogonal(QLearnSuperClass):

    def __init__(self):
        super(QLearnTurnOrthogonal,self).__init__()
        self.actions = [0, 1, 2]
        self.Q = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.states = [0,1,2,3]
        self.gamma = 0.8
        self.dist = QLearnDistOrthogonal()
        self.lift = QLearnLiftOrthogonal()
        self.maxAction = 0
        self.rate = 0.3
        self.totalScore = 0

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
            elif x == 2:
                currentState = 2
            else:
                currentState = None
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
        nextActRand = randint(0,len(self.actions)-1)
        await self.robotMovement(nextActRand,robot)
        global nextActionIndex
        nextActionIndex = nextActRand

    async def currentStateEvaluation(self,robot:cozmo.robot.Robot,voice):
        currentState = await self.findCurrentState(robot)
        if currentState != None:
            maxValue = np.max(self.Q[currentState][:])
            await self.nextAction(robot)
            await robot.say_text("What did you think?").wait_for_completed()
            await voice.voiceComms()
            print("This is the code words " + voice.speech)
            if "good".lower() in voice.speech:
                self.Q[currentState][nextActionIndex] = (1-self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * round(3 + self.gamma * maxValue))
                await robot.say_text("Perfect").wait_for_completed()
            elif "medium".lower() in voice.speech:
                self.Q[currentState][nextActionIndex] = (1-self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * round(1 + self.gamma * maxValue))
                await robot.say_text("Noted").wait_for_completed()
            elif "bad".lower() in voice.speech:
                self.Q[currentState][nextActionIndex] = (1-self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * round(-3 + self.gamma * maxValue))
                await robot.say_text("Has to be improved").wait_for_completed()
            else:
                await robot.say_text("Sorry I didn't hear anything").wait_for_completed()
            print(str(self.Q))
            print("This is the basic Q Matrix " + str(self.Q))
        else:
            await robot.say_text("Sorry, I didnt find your face, please try putting it in my vision for best results").wait_for_completed()
    time.sleep(2)

    async def currentStateEvaluationTest(self, robot: cozmo.robot.Robot):
        currentState = await self.findCurrentState(robot)
        if currentState != None:
            await self.nextActionMax(currentState, robot)
            self.totalScore = self.totalScore + self.Q[currentState][self.maxAction]
            print(str(self.totalScore))
            print("This is the basic Q Matrix " + str(self.Q))
        else:
            await robot.say_text("Sorry, I don't know my position").wait_for_completed()
        time.sleep(2)

    async def nextActionMax(self,currentState, robot:cozmo.robot.Robot):
        self.maxAction = np.where(self.Q[currentState][:] == np.max(self.Q[currentState][:]))
        self.maxAction = np.amax(self.maxAction[0])
        await self.robotMovement(self.maxAction, robot)
        return self.maxAction

    async def trainCozmo(self,robot:cozmo.robot.Robot,voice,backVoice):
        await robot.say_text("I'm training when I am upside down").wait_for_completed()
        for i in range(20):
            if "Move".lower() in backVoice.speech.lower() or "Stop".lower() in backVoice.speech.lower():
                if "Cozmo".lower() in backVoice.speech.lower() or "Cosmo".lower() in backVoice.speech.lower():
                    print("RUNNING TRAIN SPEECH MOVES")
                    await super().speechCheck(robot,voice,backVoice)
                    backVoice.speech = ""
            else:
                print("RUNNING NORMAL MOVES")
                await self.currentStateEvaluation(robot,voice)

    async def testCozmo(self,robot:cozmo.robot.Robot,voice):
        print(voice.speech)
        if "Move".lower() in voice.speech.lower() or "Stop".lower() in voice.speech.lower():
            if "Cosmo".lower() in voice.speech.lower() or "Cozmo".lower() in voice.speech.lower():
                print("RUNNING TEST SPEECH MOVES")
                await super().speechCheckTest(robot,voice)
                voice.speech = ""
        else:
            print("THE BEST NORMAL MOVE")
            await self.currentStateEvaluationTest(robot)





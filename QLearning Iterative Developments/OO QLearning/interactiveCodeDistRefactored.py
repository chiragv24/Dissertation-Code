import cozmo
import asyncio
from cozmo.util import distance_mm, speed_mmps, degrees
from random import randint
import re
import numpy as np
from tkinter import *
import time
import abc
from matplotlib import pyplot
import matplotlib
import threading
from threading import Thread
from microIntegrationInteractive import voiceIntegration

class QLearnSuperClass(abc.ABC):
    nextActionIndex = 0

    def __init__(self):
        self.initState = 0
        self.gamma = 0.5
        self.nextActIndex = 0
        self.Q = []
        self.states = []
        self.rewards = [1, 0, -1]
        self.rate = 0.3
        self.voice = voiceIntegration()

    @abc.abstractmethod
    def robotMovement(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    async def nextAction(self, *args, **kwargs):
        pass

    def update(self, currentState, action, gamma):
        maxValue = np.max(self.Q[currentState][:])
        rating = 0
        self.Q[currentState][action] = round((1 - self.rate) * self.Q[currentState][action] + (self.rate * round(self.rewards[rating] + gamma * maxValue, 2),2))

    @abc.abstractmethod
    def findCurrentState(self, robot: cozmo.robot.Robot):
        pass

    @abc.abstractmethod
    def trainCozmo(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def testCozmo(self, *args, **kwargs):
        pass

    def startLoop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeThread(self):
        newLoop = asyncio.new_event_loop()
        t = Thread(target=self.startLoop, args=(newLoop,), daemon=True)
        t.start()
        newLoop.call_soon_threadsafe(self.voice.voiceComms)
        return t

    async def scoringSystem(self,robot:cozmo.robot.Robot,state,action,maxValue,voice):
        compMed = re.search(r"\bok", voice.speech)
        compBad = re.search(r"ad\b", voice.speech)
        compGood = re.search(r"ood\b", voice.speech)
        await robot.say_text("What did you think?").wait_for_completed()
        while voice.clearSpeech == False:
            await voice.voiceComms()
        if compGood:
            await robot.say_text("Perfect").wait_for_completed()
            self.Q[state][action] = (1 - self.rate) * self.Q[state][action] + (self.rate * (3 + self.gamma * maxValue))
        elif compMed:
            await robot.say_text("Noted").wait_for_completed()
            self.Q[state][action] = (1 - self.rate) * self.Q[state][action] + (self.rate * (self.gamma * maxValue))
        elif compBad:
            await robot.say_text("Has to be improved").wait_for_completed()
            self.Q[state][action] = (1 - self.rate) * self.Q[state][action] + (self.rate * (-3 - self.gamma * maxValue))
        print("This is the move Q Matrix " + str(voice.QMove))

    async def voiceMove(self, robot: cozmo.robot.Robot, action):
        await robot.say_text("Move command").wait_for_completed()
        if action == 0:
            await robot.drive_straight(distance_mm(-150), speed_mmps(50)).wait_for_completed()
        elif action == 2:
            await robot.drive_straight(distance_mm(150), speed_mmps(50)).wait_for_completed()
        elif action == 1:
            await robot.say_text("Sure?").wait_for_completed()
        elif action == 3:
            await robot.say_text("Idle").wait_for_completed()

    async def speechCheck(self, robot: cozmo.robot.Robot, voice, backVoice):
        print("This is the voice speech " + backVoice.speech)
        compMove = re.search(r"ove\b", backVoice.speech)
        compStop = re.search(r"top\b", backVoice.speech)
        compMed = re.search(r"\bok", voice.speech)
        compBad = re.search(r"ad\b", voice.speech)
        compGood = re.search(r"ood\b", voice.speech)
        # compMed = re.search(r"\bok", backVoice.speech)
        # compBad = re.search(r"ad\b", backVoice.speech)
        # compGood = re.search(r"ood\b", backVoice.speech)
        if compMove:
            print("It is doing the voice methods now")
            dist = await self.findCurrentState(robot)
            randomAction = randint(0, 3)
            await self.voiceMove(robot, randomAction)
            maxValue = np.max(voice.QMove[dist][:])
            self.scoringSystem(robot,dist,randomAction,maxValue,)
            # # Updating the Q matrix for the voice + distance orthogonal
            # await robot.say_text("What did you think?").wait_for_completed()
            # while voice.clearSpeech == False:
            #     await voice.voiceComms()
            # if compGood:
            #     await robot.say_text("Perfect").wait_for_completed()
            #     self.Q[dist][randomAction] = (1 - self.rate) * self.Q[dist][randomAction] + (self.rate * (3 + self.gamma * maxValue))
            # elif compMed:
            #     await robot.say_text("Noted").wait_for_completed()
            #     self.Q[dist][randomAction] = (1 - self.rate) * self.Q[dist][randomAction] + (self.rate * (self.gamma * maxValue))
            # elif compBad:
            #     await robot.say_text("Has to be improved").wait_for_completed()
            #     self.Q[dist][randomAction] = (1 - self.rate) * self.Q[dist][randomAction] + (self.rate * (-3 - self.gamma * maxValue))
            # print("This is the move Q Matrix " + str(voice.QMove))
        elif compStop:
            await robot.say_text("Stop command").wait_for_completed()
            randomAction = randint(0, 1)
            maxValue = np.max(voice.QStop)
            if randomAction == 1:
                await robot.say_text("Stopping now").wait_for_completed()
            else:
                await robot.say_text("Not obeying").wait_for_completed()
            await robot.say_text("What did you think?").wait_for_completed()
            while voice.clearSpeech == False:
                await voice.voiceComms()
            if compGood:
                await robot.say_text("Perfect").wait_for_completed()
                voice.QStop[randomAction] = round((1 - self.rate) * voice.QStop[randomAction] + (self.rate * 1 + self.gamma * maxValue), 2)
            elif compMed:
                await robot.say_text("Noted").wait_for_completed()
                voice.QStop[randomAction] = round((1 - self.rate) * voice.QStop[randomAction] + (self.rate + self.gamma * maxValue), 2)
            elif compBad:
                await robot.say_text("Has to be improved").wait_for_completed()
                voice.QStop[randomAction] = round((1 - self.rate) * voice.QStop[randomAction] + (self.rate * -self.gamma * maxValue), 2)
            print("This is the stop Q Matrix " + str(voice.QStop))

    async def speechCheckTest(self, robot: cozmo.robot.Robot, voice):
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
        super(QLearnDistOrthogonal, self).__init__()
        self.actions = [0, 1, 2, 3]
        self.Q = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.roundQ =  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        self.states = [0, 1, 2]
        self.gamma = 0.5
        self.initState = 0
        self.nextActIndex = 0
        self.voice = voiceIntegration()
        self.loop = asyncio.get_event_loop()
        self.maxAction = 0
        self.totalScore = 0
        self.rate = 0.3
        self.cubeDist = 0
        self.cubeMoved = False
        self.faceDist = 0

    async def nextAction(self, currentState, robot: cozmo.robot.Robot):
        nextActRand = randint(0, 3)
        await self.robotMovement(nextActRand, currentState, robot)
        global nextActionIndex
        nextActionIndex = nextActRand


    async def robotMovement(self, actionNum, currentState, robot: cozmo.robot.Robot):
        distToMove = 0
        if not currentState==2:
            self.cubeDist = await self.findTheCube(robot)
        if(currentState == 2 and actionNum == 1):
            if self.cubeDist == None:
                await robot.say_text("Too close").wait_for_completed()
            else:
                print("This is the currentState and the action " + str(actionNum) + " " + str(currentState))
                distFromFrontOfCube = self.cubeDist - 43
                await robot.say_text("Moving forward").wait_for_completed()
                distToMove = distFromFrontOfCube - 35
                if distToMove < 10:
                    distToMove = 10
            await robot.drive_straight(distance_mm(distToMove),speed_mmps(50)).wait_for_completed()
        elif (actionNum == 0):
                print("Moved backwards")
                await robot.say_text("Moving back").wait_for_completed()
                await robot.drive_straight(distance_mm(-350), speed_mmps(75)).wait_for_completed()
                return "moving backwards"
        elif (actionNum == 1):
            if self.cubeDist == None:
                distToMove = 175
            elif self.cubeDist > 350:
                distToMove = 350
            else:
                distToMove = self.cubeDist - 35
            print("Moved forward")
            await robot.say_text("Moving forward").wait_for_completed()
            await robot.drive_straight(distance_mm(distToMove), speed_mmps(75)).wait_for_completed()
            return "moving forwards"
        elif (actionNum == 2):
            print("Greeted")
            await robot.say_text("Hello how are you doing today?").wait_for_completed()
            return "greeting"
        else:
            print("idle")
            await robot.say_text("Idle").wait_for_completed()
            return "idle"

    async def moveRobotHead(self, robot: cozmo.robot.Robot):
        robot.move_lift(-3)

    async def secondTest(self,robot:cozmo.robot.Robot):
        face = None
        await robot.set_head_angle(degrees(30)).wait_for_completed()
        while True:
                if face and face.is_visible:
                    print("kobe")
                    for face in robot.world.visible_faces:
                        await robot.say_text("Face found").wait_for_completed()
                        self.faceDist = abs(face.pose.position.x - robot.pose.position.x)
                        if self.faceDist < float(850) and self.faceDist > float(250):
                            await robot.say_text("Ideal position").wait_for_completed()
                            print("This is the distance from the face " + str(self.faceDist))
                            currentState = 1
                        elif self.faceDist > float(850):
                            await robot.say_text("I´m far").wait_for_completed()
                            print("This is the distance from the face " + str(self.faceDist))
                            currentState = 0
                        else:
                            await robot.say_text("I'm close").wait_for_completed()
                            print("This is the distance from the face " + str(self.faceDist))
                            currentState = 2
                        return currentState
                else:
                    try:
                        await robot.drive_straight(distance_mm(100),speed_mmps(100)).wait_for_completed()
                        await robot.set_head_angle(degrees(30)).wait_for_completed()
                        face = await robot.world.wait_for_observed_face(timeout=5)
                    except asyncio.TimeoutError:
                        print("Timeout")

    def handleCubeMove(self,evt,**kw):
        print("Object %s stopped moving: duration=%.1f seconds" % (evt.obj.object_id, evt.move_duration))
        self.cubeMoved = True

    def detectIfFarOrClose(self,robot:cozmo.robot.Robot):
        robot.add_event_handler(cozmo.objects.EvtObjectMovingStopped,self.handleCubeMove)

    def cubeDistanceMove(self,robot:cozmo.robot.Robot):
        if self.cubeMoved:


    async def searchForFace(self, robot: cozmo.robot.Robot):
        self.cubeMoved = False
        face = None
        await robot.set_head_angle(degrees(30)).wait_for_completed()
        while True:
            if face and face.is_visible:
                for face in robot.world.visible_faces:
                    await robot.say_text("Face found").wait_for_completed()
                    self.faceDist = abs(face.pose.position.x - robot.pose.position.x)
                    if self.faceDist < float(850) and self.faceDist > float(250):
                        await robot.say_text("Ideal position").wait_for_completed()
                        print("This is the distance from the face " + str(self.faceDist))
                        currentState = 1
                    elif self.faceDist > float(850):
                        await robot.say_text("I'm far").wait_for_completed()
                        print("This is the distance from the face " + str(self.faceDist))
                        currentState = 0
                    else:
                        await robot.say_text("I'm close").wait_for_completed()
                        print("This is the distance from the face " + str(self.faceDist))
                        currentState = 2
                    return currentState
            else:
                try:
                    face = await robot.world.wait_for_observed_face(timeout=5)
                except asyncio.TimeoutError:
                    await robot.say_text("Using cube position").wait_for_completed()
                    self.cubeDist = await self.findTheCube(robot)
                    if self.cubeDist != None:
                        if self.cubeDist < 250:
                            currentState = 2
                            await robot.say_text("I'm close").wait_for_completed()
                            return currentState
                        elif self.cubeDist > 850:
                            currentState = 0
                            await robot.say_text("I'm far").wait_for_completed()
                            return currentState
                        else:
                            currentState = 1
                            await robot.say_text("Ideal position").wait_for_completed()
                            return currentState
                    else:
                        try:
                            self.detectIfFarOrClose(robot)
                            await robot.drive_straight(distance_mm(100),speed_mmps(50)).wait_for_completed()
                            print("THIS IS IF THE CUBE HAS BEEN MOVED AT ANY POINT " + str(self.cubeMoved))
                            if self.cubeMoved == True:
                                currentState = 2
                                await robot.say_text("I'm close").wait_for_completed()
                                return currentState
                            else:
                                await robot.say_text("I'm far").wait_for_completed()
                                currentState = await self.secondTest(robot)
                                return currentState
                        except asyncio.TimeoutError:
                            print("Time out")


    async def findCurrentState(self, robot: cozmo.robot.Robot):
        await self.moveRobotHead(robot)
        face = await self.searchForFace(robot)
        return face

    async def nextActionMax(self, currentState, robot: cozmo.robot.Robot):
        # THE ACTION THAT IS CARRIED OUT HAS TO BE THE ONE WITH THE HIGHEST SCORE IN THAT SPECIFIC STATE
        self.maxAction = np.where(self.Q[currentState][:] == np.max(self.Q[currentState][:]))
        self.maxAction = np.amax(self.maxAction[0])
        await self.robotMovement(self.maxAction, currentState, robot)
        return self.maxAction

    async def findTheCube(self, robot: cozmo.robot.Robot):
        await robot.set_head_angle(degrees(-15)).wait_for_completed()
        try:
            cube = await robot.world.wait_for_observed_light_cube(timeout=10)
            x = cube.pose.position.x
            dist = abs(robot.pose.position.x - x)
        except asyncio.TimeoutError:
            dist = None
        print(dist)
        return dist

    async def trainCozmo(self, robot: cozmo.robot.Robot, voice, backVoice):
            await robot.say_text("Training phase").wait_for_completed()
            for i in range(50):
                compMove = re.search(r"ove\b", backVoice.speech)
                compStop = re.search(r"top\b", backVoice.speech)
                compGood = None
                compMed = None
                compBad = None
                print("THIS IS THE BACK VOICE " + backVoice.speech)
                if compMove or compStop:
                    await super().speechCheck(robot, voice, backVoice)
                    backVoice.speech = ""
                print("This is train loop " + str(i))
                currentState = await self.findCurrentState(robot)
                print("This is the final state " +  str(currentState))
                if currentState != None:
                    maxValue = np.max(self.Q[currentState][:])
                    await self.nextAction(currentState, robot)
                    await robot.say_text("What did you think?").wait_for_completed()
                    try:
                        count = 0
                        while voice.clearSpeech == False or compMed == None and compGood == None and compBad == None:
                            count = count + 1
                            if count >=2:
                                await robot.say_text("Score please").wait_for_completed()
                            await asyncio.wait_for(voice.voiceComms(), 10)
                            compMed = re.search(r"\bok",voice.speech)
                            compBad= re.search(r"ad\b",voice.speech)
                            compGood = re.search(r"ood\b",voice.speech)
                        voice.clearSpeech = False
                        print("This is the code words " + voice.speech)
                        if compGood:
                            self.Q[currentState][nextActionIndex] = (1 - self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * (3 + self.gamma * maxValue))
                            self.roundQ[currentState][nextActionIndex] = round((1 - self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * (3 + self.gamma * maxValue)),2)
                            await robot.say_text("Perfect").wait_for_completed()
                            await robot.play_anim("anim_memorymatch_successhand_cozmo_01").wait_for_completed()
                        if compMed:
                            self.Q[currentState][nextActionIndex] = (1 - self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * (self.gamma * maxValue))
                            self.roundQ[currentState][nextActionIndex] = round((1 - self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * (self.gamma * maxValue)), 2)
                            await robot.say_text("Noted").wait_for_completed()
                            await robot.play_anim("anim_memorymatch_reacttopattern_standard_01").wait_for_completed()
                        elif compBad:
                            self.Q[currentState][nextActionIndex] = (1 - self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * (-3 - self.gamma * maxValue))
                            self.roundQ[currentState][nextActionIndex] = round((1 - self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * (-3 - self.gamma * maxValue)), 2)
                            await robot.say_text("Not Good").wait_for_completed()
                            await robot.play_anim("anim_memorymatch_failhand_01").wait_for_completed()
                        print(str(self.Q))

                    except asyncio.TimeoutError:
                        await robot.say_text("Sorry not heard").wait_for_completed()
                else:
                    await robot.say_text("Sorry no face found").wait_for_completed()
            await self.testCozmo(robot,backVoice)

    async def testCozmo(self, robot: cozmo.robot.Robot, voice):
        await robot.say_text("Testing phase").wait_for_completed()
        for i in range(50):
            if "Move".lower() in voice.speech.lower() or "Stop".lower() in voice.speech.lower():
                    await super().speechCheckTest(robot, voice)
                    voice.speech = ""
            else:
                currentState = await self.findCurrentState(robot)
                if currentState != None:
                    await self.nextActionMax(currentState, robot)
                    self.totalScore = self.totalScore + self.Q[currentState][self.maxAction]
                else:
                    await robot.say_text("Sorry no face found").wait_for_completed()



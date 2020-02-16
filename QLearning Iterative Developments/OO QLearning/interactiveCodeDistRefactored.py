import cozmo
import asyncio
from cozmo.util import distance_mm, speed_mmps, degrees
from random import randint
import re
import numpy as np
from tkinter import *
import abc
from microIntegrationInteractive import voiceIntegration

class QLearnSuperClass(abc.ABC):
    nextActionIndex = 0

    def __init__(self):
        self.initState = 0
        self.gamma = 0.5
        self.nextActIndex = 0
        self.Q = []
        self.states = []
        self.rewards = [3, 0, -3]
        self.rate = 0.3

    @abc.abstractmethod
    def robotMovement(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    async def nextAction(self, *args, **kwargs):
        pass

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

    def scoringSystem(self,state,action,maxValue,reward):
        if reward >= 0:
            self.Q[state][action] = (1 - self.rate) * self.Q[state][action] + (self.rate * (reward + self.gamma * maxValue))
        else:
            self.Q[state][action] = (1 - self.rate) * self.Q[state][action] + (self.rate * (reward - self.gamma * maxValue))
        print(str(self.Q))

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

    async def voiceScore(self,voice,robot:cozmo.robot.Robot):
        compGood = None
        compMed = None
        compBad = None
        count = 0
        while voice.clearSpeech == False or compMed == None and compGood == None and compBad == None:
            count = count + 1
            if count >= 2:
                await robot.say_text("Score please").wait_for_completed()
            await asyncio.wait_for(voice.voiceComms(), 10)
            compMed = re.search(r"\bok", voice.speech)
            compBad = re.search(r"ad\b", voice.speech)
            compGood = re.search(r"ood\b", voice.speech)
        voice.clearSpeech = False
        print("This is the code words " + voice.speech)
        return compGood,compMed,compBad

    async def scoreMoves(self,scores,robot:cozmo.robot.Robot,state,action,maxValue):
        if scores[0]:
            await robot.say_text("Perfect").wait_for_completed()
            await robot.play_anim("anim_memorymatch_successhand_cozmo_01").wait_for_completed()
            self.scoringSystem(state,action,maxValue,self.rewards[0])
        elif scores[1]:
            #self.roundQ[currentState][nextActionIndex] = round((1 - self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * (self.gamma * maxValue)), 2)
            await robot.say_text("Noted").wait_for_completed()
            await robot.play_anim("anim_memorymatch_reacttopattern_standard_01").wait_for_completed()
            self.scoringSystem(state,action,maxValue,self.rewards[1])
        elif scores[2]:
            await robot.say_text("Not Good").wait_for_completed()
            await robot.play_anim("anim_memorymatch_failhand_01").wait_for_completed()
            self.scoringSystem(state,action,maxValue,self.rewards[2])

    async def speechCheck(self, robot: cozmo.robot.Robot, voice, backVoice):
        print("This is the voice speech " + backVoice.speech)
        compMove = re.search(r"ove\b", backVoice.speech)
        compStop = re.search(r"top\b", backVoice.speech)
        if compMove:
            print("It is doing the voice methods now")
            state = await self.findCurrentState(robot)
            randomAction = randint(0, 3)
            await robot.say_text("What did you think?").wait_for_completed()
            await self.voiceMove(robot, randomAction)
            maxValue = np.max(voice.QMove[state][:])
            score = await self.voiceScore(voice,robot)
            await self.scoreMoves(score,robot,state,randomAction,maxValue)
        elif compStop:
            await robot.say_text("Stop command").wait_for_completed()
            randomAction = randint(0, 1)
            if randomAction == 1:
                await robot.say_text("Stopping now").wait_for_completed()
            else:
                await robot.say_text("Not obeying").wait_for_completed()
                await robot.drive_straight(distance_mm(50),speed_mmps(50)).wait_for_completed()
            maxValue = np.max(voice.QStop)
            score = await self.voiceScore(voice,robot)
            await self.scoreMoves(score,robot,3,randomAction,maxValue)

    async def speechCheckTest(self, robot: cozmo.robot.Robot, voice):
        print("This is the voice speech " + voice.speech)
        compMove = re.search(r"ove\b", voice.speech)
        compStop = re.search(r"top\b", voice.speech)
        if compMove:
            dist = await self.findCurrentState(robot)
            self.maxAction = np.where(self.Q[dist][:] == np.max(self.Q[dist][:]))
            print(self.maxAction)
            self.maxAction = np.amax(self.maxAction[0])
            await self.voiceMove(robot, self.maxAction)
            self.totalScore = self.totalScore + self.Q[dist][self.maxAction]
        elif compStop:
            maxStop = np.amax(self.Q[3])
            if maxStop == 1:
                await robot.say_text("Stopping now").wait_for_completed()
            else:
                await robot.say_text("No obeying").wait_for_completed()
            self.totalScore = self.totalScore + self.Q[3][maxStop]
            print(str(self.totalScore))


###############################################################################################################################################

class QLearnDistOrthogonal(QLearnSuperClass):
    nextActionIndex = 0

    def __init__(self):
        super(QLearnDistOrthogonal, self).__init__()
        self.actions = [0, 1, 2, 3]
        self.Q = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0]]
        self.states = [0, 1, 2]
        self.nextActIndex = 0
        self.voice = voiceIntegration()
        self.loop = asyncio.get_event_loop()
        self.maxAction = 0
        self.totalScore = 0
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
                distToMove = distFromFrontOfCube - 25
                if distToMove < 10:
                    distToMove = 10
            await robot.drive_straight(distance_mm(distToMove),speed_mmps(50)).wait_for_completed()
        elif (actionNum == 0):
                print("Moved backwards")
                await robot.say_text("Moving back").wait_for_completed()
                await robot.drive_straight(distance_mm(-350), speed_mmps(75)).wait_for_completed()
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
        elif (actionNum == 2):
            print("Greeted")
            await robot.say_text("Hello how are you doing today?").wait_for_completed()
        else:
            print("idle")
            await robot.say_text("Idle").wait_for_completed()

    async def moveRobotHead(self, robot: cozmo.robot.Robot):
        robot.move_lift(-3)

    async def searchForFace(self,robot:cozmo.robot.Robot):
        while True:
            try:
                await robot.set_head_angle(degrees(30)).wait_for_completed()
                face = await robot.world.wait_for_observed_face(timeout=5)
                self.cubeMoved = False
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
                    self.detectIfFarOrClose(robot)
                    await robot.drive_straight(distance_mm(100), speed_mmps(100)).wait_for_completed()
                    if self.cubeMoved == True:
                        currentState = 2
                        await robot.say_text("I'm close").wait_for_completed()
                        return currentState
                    print("Timeout")

    def handleCubeMove(self,evt,**kw):
        print("Object %s stopped moving: duration=%.1f seconds" % (evt.obj.object_id, evt.move_duration))
        self.cubeMoved = True

    def detectIfFarOrClose(self,robot:cozmo.robot.Robot):
        robot.add_event_handler(cozmo.objects.EvtObjectMovingStopped,self.handleCubeMove)

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
            cube = await robot.world.wait_for_observed_light_cube(timeout=5)
            x = cube.pose.position.x
            dist = abs(robot.pose.position.x - x)
        except asyncio.TimeoutError:
            dist = None
        print(dist)
        return dist

    async def trainCozmo(self, robot: cozmo.robot.Robot, voice, backVoice):
            await robot.say_text("Training phase").wait_for_completed()
            for i in range(15):
                compMove = re.search(r"ove\b", backVoice.speech)
                compStop = re.search(r"top\b", backVoice.speech)
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
                        score = await self.voiceScore(voice,robot)
                        await self.scoreMoves(score,robot,currentState,nextActionIndex,maxValue)
                    except asyncio.TimeoutError:
                        await robot.say_text("Sorry not heard").wait_for_completed()
                else:
                    await robot.say_text("Sorry no face found").wait_for_completed()
            await self.testCozmo(robot,backVoice)

    async def testCozmo(self, robot: cozmo.robot.Robot, voice):
        await robot.say_text("Testing phase").wait_for_completed()
        for i in range(50):
            compMove = re.search(r"ove\b", voice.speech)
            compStop = re.search(r"top\b", voice.speech)
            if compMove or compStop:
                    await super().speechCheckTest(robot, voice)
                    voice.speech = ""
            else:
                currentState = await self.findCurrentState(robot)
                if currentState != None:
                    await self.nextActionMax(currentState, robot)
                    self.totalScore = self.totalScore + self.Q[currentState][self.maxAction]
                else:
                    await robot.say_text("Sorry no face found").wait_for_completed()



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
        self.gamma = 0.8
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
        self.Q[currentState][action] = round((1 - self.rate) * self.Q[currentState][action] + (self.rate * round(self.rewards[rating] + gamma * maxValue, 2),2)

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

    async def voiceMove(self, robot: cozmo.robot.Robot, action):
        await robot.say_text("I'm going to be acting based on your preferences now").wait_for_completed()
        if action == 0:
            await robot.drive_straight(distance_mm(-150), speed_mmps(50)).wait_for_completed()
        elif action == 2:
            await robot.drive_straight(distance_mm(150), speed_mmps(50)).wait_for_completed()
        elif action == 1:
            await robot.say_text("Are you sure you want me to move?").wait_for_completed()
        elif action == 3:
            await robot.say_text("I'm not moving this time").wait_for_completed()

    async def speechCheck(self, robot: cozmo.robot.Robot, voice, backVoice):
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
            while voice.clearSpeech == False:
                await voice.voiceComms()
            if "good" in voice.speech.lower():
                await robot.say_text("Perfect").wait_for_completed()
                voice.QMove[dist][randomAction] = round((1 - self.rate) * voice.QMove[dist][randomAction] + (self.rate * 3 + self.gamma * maxValue), 2)
            elif "medium" in voice.speech.lower():
                voice.QMove[dist][randomAction] = round((1 - self.rate) * voice.QMove[dist][randomAction] + (self.rate + self.gamma * maxValue), 2)
                await robot.say_text("Noted").wait_for_completed()
            elif "bad" in voice.speech.lower():
                await robot.say_text("Has to be improved").wait_for_completed()
                voice.QMove[dist][randomAction] = round((1 - self.rate) * voice.QMove[dist][randomAction] + (self.rate * -3 + self.gamma * maxValue), 2)
            print("This is the move Q Matrix " + str(voice.QMove))
        elif "Stop".lower() in backVoice.speech.lower():
            await robot.say_text("Acting based on your word stop").wait_for_completed()
            randomAction = randint(0, 1)
            maxValue = np.max(voice.QStop)
            if randomAction == 1:
                await robot.say_text("Sorry, I am stopping now").wait_for_completed()
            else:
                await robot.say_text("I'm not moving thsi time").wait_for_completed()
            await robot.say_text("What did you think?").wait_for_completed()
            await voice.voiceComms()
            if "good" in voice.speech.lower():
                await robot.say_text("Perfect").wait_for_completed()
                voice.QStop[randomAction] = round((1 - self.rate) * voice.QStop[randomAction] + (self.rate * 3 + self.gamma * maxValue), 2)
            elif "medium" in voice.speech.lower():
                await robot.say_text("Noted").wait_for_completed()
                voice.QStop[randomAction] = round((1 - self.rate) * voice.QStop[randomAction] + (self.rate + self.gamma * maxValue), 2)
            elif "bad" in voice.speech.lower():
                await robot.say_text("Has to be improved").wait_for_completed()
                voice.QStop[randomAction] = round((1 - self.rate) * voice.QStop[randomAction] + (self.rate * -3 + self.gamma * maxValue), 2)
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
        self.states = [0, 1, 2]
        self.gamma = 0.8
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
        if not currentState == 2:
            facialExp = await self.facialExpressionEstimate(robot)
        else:
            facialExp = "Unknown"
        await self.robotMovement(nextActRand, facialExp, currentState, robot)
        global nextActionIndex
        nextActionIndex = nextActRand


    async def robotMovement(self, actionNum, facialExp, currentState, robot: cozmo.robot.Robot):
        print("This is the currentState and the action " + str(actionNum) + " " + str(currentState))
        distToMove = 0
        if(currentState == 2 and actionNum == 1):
            if self.cubeDist == None:
                #ASK MATTHIAS IF WORTH MAKING THIS ANOTHER MATRIX AND DECIDE IF TO TIP AND NOT TO TIP AND THEN SOCIAL DOESNT TIP
                await robot.say_text("I'm too close to the cube, I will tip it").wait_for_completed()
            else:
            # Cube measured from middle so the dist to the beginning is 21.5cm less
                distFromFrontOfCube = self.cubeDist - 43
                await robot.say_text("I moving slightly forward").wait_for_completed()
                distToMove = distFromFrontOfCube - 35
                if distToMove < 10:
                    distToMove = 10
            await robot.drive_straight(distance_mm(distToMove),speed_mmps(50)).wait_for_completed()
        elif (currentState == 0 and facialExp == "happy"):
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
            if self.cubeDist == None or self.cubeDist > 350:
                distToMove = 350
            else:
                distToMove = self.cubeDist - 35
            print("Moved forward")
            await robot.say_text("I'm moving forward now").wait_for_completed()
            await robot.drive_straight(distance_mm(distToMove), speed_mmps(75)).wait_for_completed()
            return "moving forwards"
        elif (actionNum == 2):
            print("Greeted")
            await robot.say_text("Hello how are you doing today?").wait_for_completed()
            return "greeting"
        else:
            print("idle")
            await robot.say_text("I'm not moving this time").wait_for_completed()
            return "idle"

    async def facialExpressionEstimate(self, robot: cozmo.robot.Robot):
        face = None
        while True:
            if face and face.is_visible:
                robot.enable_facial_expression_estimation(True)
                expEst = face.expression
                print("This is the expression " + expEst)
                if expEst.lower() == "Unknown".lower():
                    print("No recognition")
                else:
                    await robot.say_text("Facial expression analysed, as " + str(face.expression)).wait_for_completed()
                return face.expression
            else:
                try:
                    face = await robot.world.wait_for_observed_face(timeout=5)
                except asyncio.TimeoutError:
                    await robot.say_text("Sorry I couldn't estimate your expression").wait_for_completed()
                    print("Didn't find a face.")
                    return

    async def moveRobotHead(self, robot: cozmo.robot.Robot):
        robot.move_lift(-3)

    async def secondTest(self,robot:cozmo.robot.Robot):
        face = None
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
            except:
                print("This is not working")

    def handleCubeMove(self,evt,**kw):
        #print("Object %s started moving: acceleration=%s" %(evt.obj.object_id, evt.acceleration))
        print("Object %s stopped moving: duration=%.1f seconds" % (evt.obj.object_id, evt.move_duration))
        self.cubeMoved = True

    def detectIfFarOrClose(self,robot:cozmo.robot.Robot):
        robot.add_event_handler(cozmo.objects.EvtObjectMovingStopped,self.handleCubeMove)
        #robot.add_event_handler(cozmo.objects.EvtObjectMovingStarted,self.handleCubeMove)

        #self.cubeMoved = True

    async def searchForFace(self, robot: cozmo.robot.Robot):
        self.cubeDist = await self.findTheCube(robot)
        self.cubeMoved = False
        face = None
        await robot.set_head_angle(degrees(30)).wait_for_completed()
        #while not face == None:
        while True:
            if face and face.is_visible:
                for face in robot.world.visible_faces:
                    self.faceDist = abs(face.pose.position.x - robot.pose.position.x)
                    if self.faceDist < float(850) and self.faceDist > float(250):
                        await robot.say_text("I'm currently in the optimal state").wait_for_completed()
                        print("This is the distance from the face " + str(self.faceDist))
                        currentState = 1
                    elif self.faceDist > float(850):
                        await robot.say_text("I´m currently in the far state").wait_for_completed()
                        print("This is the distance from the face " + str(self.faceDist))
                        currentState = 0
                    else:
                        await robot.say_text("I'm currently in the close state").wait_for_completed()
                        print("This is the distance from the face " + str(self.faceDist))
                        currentState = 2
                    return currentState
            else:
                try:
                    face = await robot.world.wait_for_observed_face(timeout=10)
                except asyncio.TimeoutError:
                    await robot.say_text("Sorry I didn't find your face, using the cube position instead").wait_for_completed()
                    if self.cubeDist != None:
                        if self.cubeDist < 250:
                            currentState = 2
                            await robot.say_text("I'm currently in the close state").wait_for_completed()
                            return currentState
                        elif self.cubeDist > 850:
                            currentState = 0
                            await robot.say_text("I'm currently in the far state").wait_for_completed()
                            return currentState
                        else:
                            currentState = 1
                            await robot.say_text("I'm currently in the optimal state").wait_for_completed()
                            return currentState
                    else:
                        try:
                            #poseBef = cozmo.objects.LightCube
                            #print("POSE BEF " + str(poseBef))
                            self.detectIfFarOrClose(robot)
                            await robot.drive_straight(distance_mm(100),speed_mmps(50)).wait_for_completed()
                            #await self.detectIfFarOrClose(robot)
                            # a = cozmo.objects.LightCube.time_since_last_seen
                            # m = cozmo.objects.LightCube.last_moved_time
                            #x = cozmo.objects.LightCube.pose
                            #print("POSE AFT " + str(x))
                            print("THIS IS IF THE CUBE HAS BEEN MOVED AT ANY POINT " + str(self.cubeMoved))
                            if self.cubeMoved == True:
                                currentState = 2
                                return currentState
                            else:
                                await robot.drive_straight(distance_mm(200),speed_mmps(75)).wait_for_completed()
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
        facialExp = await self.facialExpressionEstimate(robot)
        await self.robotMovement(self.maxAction, facialExp, currentState, robot)
        return self.maxAction

    def writeToFile(self, currentState, action, reward):
        file = open('trainData.txt', mode='a')
        file.write(str(currentState) + " " + str(action) + " " + str(reward))
        file.write("\n")
        file.close()

    # async def flip(self,robot:cozmo.robot.Robot):
    #     cube = await robot.world.wait_for_observed_light_cube()
    #     print("Cozmo found a cube, and will now attempt to pop a wheelie on it")
    #     action = await robot.pop_a_wheelie(cube, num_retries=2,in_parallel=True).wait_for_completed()
    #     return action

    async def findTheCube(self, robot: cozmo.robot.Robot):
        #CHECK ALL OF THIS TOMORROW
        #print(str(robot.world.nav_memory_map.size))
        #print(str(robot.world.nav_memory_map.size)) - robot.pose.position
        #cozmo.objects.EvtObjectMovingStarted
        await robot.say_text("I'm trying to  find the cube now").wait_for_completed()
        await robot.set_head_angle(degrees(-15)).wait_for_completed()
        try:
            cube = await robot.world.wait_for_observed_light_cube(timeout=10)
            x = cube.pose.position.x
            dist = abs(robot.pose.position.x - x)
        except asyncio.TimeoutError:
            await robot.say_text("Sorry I didn't find the cube").wait_for_completed()
            dist = None
        print(dist)
        return dist

    async def trainCozmo(self, robot: cozmo.robot.Robot, voice, backVoice):
        # pyplot.figure()
        # pyplot.text(0.35, 0.5,"Close Me")
        # pyplot.show()
        open('trainData.txt', mode='w')
        await robot.say_text("I'm training my distance perception now").wait_for_completed()
        #self.spawnWindow(voice.speech,tkloop)
        for i in range(100):
            print("THIS IS THE BACK VOICE " + backVoice.speech)
            if "Move".lower() in backVoice.speech.lower() or "Stop".lower() in backVoice.speech.lower():
                #if "Cosmo" in backVoice.speech.lower() or "Cozmo".lower() in backVoice.speech.lower():
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
                    while voice.clearSpeech == False:
                        await asyncio.wait_for(voice.voiceComms(), 10)
                    voice.clearSpeech = False
                    reward = 0
                    print("This is the code words " + voice.speech)
                    compMed = re.search(r"\bmed",voice.speech)
                    compBad= re.search(r"ad\b",voice.speech)
                    compGood = re.search(r"ood\b",voice.speech)
                    if compGood:
                        bef = self.Q[currentState][nextActionIndex]
                        self.Q[currentState][nextActionIndex] = (1 - self.rate) * self.Q[currentState][
                            nextActionIndex] + (self.rate * round(3 + self.gamma * maxValue))
                        reward = self.Q[currentState][nextActionIndex] - bef
                        await robot.say_text("Perfect").wait_for_completed()
                        await robot.play_anim("anim_memorymatch_successhand_cozmo_01").wait_for_completed()
                    if compMed:
                        bef = self.Q[currentState][nextActionIndex]
                        self.Q[currentState][nextActionIndex] = (1 - self.rate) * self.Q[currentState][
                            nextActionIndex] + (self.rate * round(self.gamma * maxValue))
                        reward = self.Q[currentState][nextActionIndex] - bef
                        await robot.say_text("Noted").wait_for_completed()
                        await robot.play_anim("anim_memorymatch_reacttopattern_standard_01").wait_for_completed()
                    elif compBad:
                        bef = self.Q[currentState][nextActionIndex]
                        self.Q[currentState][nextActionIndex] = (1 - self.rate) * self.Q[currentState][
                            nextActionIndex] + (self.rate * round(-3 + self.gamma * maxValue))
                        reward = self.Q[currentState][nextActionIndex] - bef
                        await robot.say_text("Not Good").wait_for_completed()
                        await robot.play_anim("anim_memorymatch_failhand_01").wait_for_completed()
                    print(str(self.Q))
                    self.writeToFile(currentState, nextActionIndex, reward)
                    print("THIS IS THE LOGGED INFO " + str(currentState) + " " + str(nextActionIndex) + " " + str(self.Q[currentState][nextActionIndex]))
                except asyncio.TimeoutError:
                    await robot.say_text("Sorry I did not hear anything").wait_for_completed()
            else:
                await robot.say_text("Sorry I couldn't find your face").wait_for_completed()

    async def testCozmo(self, robot: cozmo.robot.Robot, voice):
        await robot.say_text("I'm going to be tested now").wait_for_completed()
        for i in range(1):
            if "Move".lower() in voice.speech.lower() or "Stop".lower() in voice.speech.lower():
                if "Cozmo".lower() in voice.speech.lower() or "Cosmo".lower() in voice.speech.lower():
                    await super().speechCheckTest(robot, voice)
                    voice.speech = ""
            else:
                currentState = await self.findCurrentState(robot)
                if currentState != None:
                    await self.nextActionMax(currentState, robot)
                    self.totalScore = self.totalScore + self.Q[currentState][self.maxAction]
                else:
                    await robot.say_text("Sorry I couldn´t find your face").wait_for_completed()
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
    def nextAction(self,*args,**kwargs):
        pass

    def update(self,currentState,action,gamma):
        maxValue = np.max(self.Q[currentState][:])
        self.Q[currentState][action] = (1 - self.rate) * self.Q[currentState][action] + (self.rate * round(self.rewards[currentState][action] + gamma * maxValue, 2))

    @abc.abstractmethod
    def findCurrentState(self):
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
        self.voice = voiceIntegration()
        self.loop = asyncio.get_event_loop()
        self.maxAction = 0
        self.totalScore = 0
        self.rate = 0.3
        self.voice.sleepTime = 20
        #self.name = "voice"

    def speechCheck(self,voice):
        print("This is the voice speech " + voice.speech)
        if "Move".lower() in voice.speech.lower():
            print("It is doing the voice methods now")
            dist =  self.findCurrentState()
            randomAction = randint(0,3)
            maxValue = np.max(voice.moveRewards[dist][:])
            # Updating the Q matrix for the voice + distance orthogonal
            voice.QMove[dist][randomAction] = (1 - self.rate) * self.Q[dist][randomAction] + (self.rate * round(voice.moveRewards[dist][randomAction] + self.gamma * maxValue, 2))
            print("This is the move Q Matrix " + str(voice.QMove))
        elif "Stop".lower() in voice.speech.lower():
            randomAction = randint(0, 1)
            maxValue = np.max(voice.stopRewards)
            voice.QStop[randomAction] = (1 - self.rate) * voice.QStop[randomAction] + (self.rate * round(voice.stopRewards[randomAction] + self.gamma * maxValue, 2))
            print("This is the stop Q Matrix " + str(voice.QStop))


    # def speechCheck(self):
    #     print("This is the voice speech " + self.voice.speech)
    #     if "Move".lower() in self.voice.speech.lower():
    #         print("It is doing the voice methods now")
    #         dist =  self.findCurrentState()
    #         randomAction = randint(0,3)
    #         maxValue = np.max(self.voice.moveRewards[dist][:])
    #         # Updating the Q matrix for the voice + distance orthogonal
    #         self.voice.QMove[dist][randomAction] = (1 - self.rate) * self.Q[dist][randomAction] + (
    #         self.rate * round(self.voice.moveRewards[dist][randomAction] + self.gamma * maxValue, 2))
    #         print("This is the move Q Matrix " + str(self.voice.QMove))
    #     elif "Stop".lower() in self.voice.speech.lower():
    #         randomAction = randint(0, 1)
    #         maxValue = np.max(self.voice.stopRewards)
    #         self.voice.QStop[randomAction] = (1 - self.rate) * self.voice.QStop[randomAction] + (
    #         self.rate * round(self.voice.stopRewards[randomAction] + self.gamma * maxValue, 2))
    #         print("This is the stop Q Matrix " + str(self.voice.QStop))

    def speechCheckTest(self,voice):
        print("This is the voice speech " + voice.speech)
        if "Move".lower() in voice.speech.lower():
            dist = self.findCurrentState()
            self.maxAction = np.where(voice.QMove[dist][:] == np.max(self.Q[dist][:]))
            self.maxAction = np.amax(self.maxAction[0])
            self.totalScore = self.totalScore + voice.QMove[dist][self.maxAction]
        elif "Stop".lower() in voice.speech.lower():
            maxStop = np.amax(voice.QStop)
            self.totalScore = self.totalScore + voice.QStop[maxStop]
            print(str(self.totalScore))

    def nextAction(self,currentState):
        nextActRand = randint(0, 3)
        global nextActionIndex
        nextActionIndex = nextActRand

    def facialExpressionEstimate(self):
        expressions = ["unknown","happy","sad","neutral","surprised","angry"]
        x = randint(0,len(expressions)-1)
        return expressions[x]

    def searchForFace(self):
        currentState = randint(0,2)
        return currentState

    def findCurrentState(self):
        face = self.searchForFace()
        return face

    def nextActionMax(self,currentState):
        #THE ACTION THAT IS CARRIED OUT HAS TO BE THE ONE WITH THE HIGHEST SCORE IN THAT SPECIFIC STATE
        self.maxAction = np.where(self.Q[currentState][:] == np.max(self.Q[currentState][:]))
        print(self.Q[currentState][:])
        print(self.maxAction)
        self.maxAction = np.amax(self.maxAction[0])
        facialExp = self.facialExpressionEstimate()
        return self.maxAction


    def trainCozmo(self,voice):
        #super().makeThread()
        for i in range(2):
            print("Speech " + voice.speech.lower())
            if "Cosmo".lower() in voice.speech.lower() or "Cozmo".lower() in voice.speech.lower():
                 self.speechCheck(voice)
                 voice.speech = ""
            else:
                currentState = self.findCurrentState()
                if currentState != None:
                    self.nextAction(currentState)
                    super().update(currentState, nextActionIndex, self.gamma)
                    print("This is the basic Q Matrix " + str(self.Q))
                else:
                    print("Sorry not found")
            print(str(i) + "finished")
            time.sleep(7)

    def testCozmo(self,voice):
        print(self.voice.speech)
        for i in range (1):
            if "Cosmo".lower() in voice.speech.lower() or "Cozmo".lower() in voice.speech.lower():
                print("RUNNING VOICE STUFF")
                self.speechCheckTest(voice)
                voice.speech = ""
            else:
                print("NOT RUNNING VOICE STUFF")
                currentState =  self.findCurrentState()
                if currentState != None:
                    self.nextActionMax(currentState)
                    self.totalScore = self.totalScore + self.Q[currentState][self.maxAction]
                    print("This is the basic Q Matrix " + str(self.Q))
                    print(str(self.totalScore))
                else:
                    print("Sorry not found this time bad score")

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
        self.voice.sleepTime = 10

    def speechCheck(self,voice):
        print("This is the voice speech " + voice.speech)
        if "Move".lower() in voice.speech.lower():
            print("It is doing the voice methods now")
            distances =  self.dist.findCurrentState()
            randomAction = randint(0,3)
            maxValue = np.max(voice.moveRewards[distances][:])
            # Updating the Q matrix for the voice + distance orthogonal
            voice.QMove[distances][randomAction] = (1 - self.rate) * self.Q[distances][randomAction] + (
            self.rate * round(voice.moveRewards[distances][randomAction] + self.gamma * maxValue, 2))
            print("This is the move Q Matrix " + str(voice.QMove))
        elif "Stop".lower() in voice.speech.lower():
            randomAction = randint(0, 1)
            maxValue = np.max(voice.stopRewards)
            voice.QStop[randomAction] = (1 - self.rate) * voice.QStop[randomAction] + (
            self.rate * round(voice.stopRewards[randomAction] + self.gamma * maxValue, 2))
            print("This is the stop Q Matrix " + str(voice.QStop))

    def speechCheckTest(self,voice):
        print("This is the voice speech " + voice.speech)
        if "Move".lower() in voice.speech.lower():
            distances = self.dist.findCurrentState()
            self.maxAction = np.where(voice.QMove[distances][:] == np.max(self.Q[distances][:]))
            self.maxAction = np.amax(self.maxAction[0])
            self.totalScore = self.totalScore + voice.QMove[distances][self.maxAction]
            print("This is the total score voicing " + str(self.totalScore))
        elif "Stop".lower() in voice.speech.lower():
            maxStop = np.amax(voice.QStop)
            self.totalScore = self.totalScore + voice.QStop[maxStop]
            print("This is the total score voicing " + str(self.totalScore))


    def findCurrentState(self):
        currentState = randint(0,3)
        return currentState

    def nextAction(self):
        nextActRand = randint(0,len(self.actions)-1)
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

    def currentStateEvaluation(self):
        currentState =  self.findCurrentState()
        if currentState != None:
            self.nextAction()
            super().update(currentState, nextActionIndex, self.gamma)
        else:
            print("This is the wrong one")
        print("THIS IS Q " + str(self.Q))
        time.sleep(5)

    def currentStateEvaluationTest(self):
        currentState =  self.findCurrentState()
        if currentState != None:
            self.nextActionMax(currentState)
            self.totalScore = self.totalScore + self.Q[currentState][self.maxAction]
            print(str(self.totalScore))
            print("This is the basic Q Matrix " + str(self.Q))
        else:
            print("No points mate")
        time.sleep(5)

    def trainCozmo(self,voice):
        #super().makeThread()
        # robot.say_text("I'm learning how to act when i'm lifted").wait_for_completed()
        for i in range (2):
            if "Cosmo".lower() in voice.speech.lower() or "Cozmo".lower() in voice.speech.lower():
                print("THIS IS TO CHECK THE CARRIED ON SPEECH")
                print(voice.speech)
                self.speechCheck(voice)
                voice.speech = ""
            else:
                 self.currentStateEvaluation()

    def nextActionMax(self,currentState):
        self.maxAction = np.where(self.Q[currentState][:] == np.max(self.Q[currentState][:]))
        self.maxAction = np.amax(self.maxAction[0])
        return self.maxAction

    def testCozmo(self,voice):
        #self.makeThread()
        # robot.say_text("I'm going to be tested now").wait_for_completed()
        for i in range (1):
            if "Cozmo".lower() in voice.speech.lower()  or "Cosmo".lower() in voice.speech.lower():
                print("RUNNING VOICE STUFF")
                self.speechCheckTest(voice)
                voice.speech = ""
            else:
                print("NOT RUUNING VOICE STUFF")
                self.currentStateEvaluationTest()

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
        self.voice.sleepTime = 10
        self.totalScore = 0
        self.rate = 0.3

    def speechCheck(self):
        print("This is the voice speech " + self.voice.speech)
        if "Move".lower() in self.voice.speech.lower():
            print("It is doing the voice methods now")
            distances =  self.dist.findCurrentState()
            randomAction = randint(0,3)
            maxValue = np.max(self.voice.moveRewards[distances][:])
            # Updating the Q matrix for the voice + distance orthogonal
            self.voice.QMove[distances][randomAction] = (1 - self.rate) * self.Q[distances][randomAction] + (
            self.rate * round(self.voice.moveRewards[distances][randomAction] + self.gamma * maxValue, 2))
            print("This is the move Q Matrix " + str(self.voice.QMove))
        elif "Stop".lower() in self.voice.speech.lower():
            randomAction = randint(0, 1)
            maxValue = np.max(self.voice.stopRewards)
            self.voice.QStop[randomAction] = (1 - self.rate) * self.voice.QStop[randomAction] + (
            self.rate * round(self.voice.stopRewards[randomAction] + self.gamma * maxValue, 2))
            print("This is the stop Q Matrix " + str(self.voice.QStop))

    def speechCheckTest(self):
        print("This is the voice speech " + self.voice.speech)
        if "Move".lower() in self.voice.speech.lower():
            distances = self.dist.findCurrentState()
            self.maxAction = np.where(self.voice.QMove[distances][:] == np.max(self.Q[distances][:]))
            self.maxAction = np.amax(self.maxAction[0])
            self.totalScore = self.totalScore + self.voice.QMove[distances][self.maxAction]
        elif "Stop".lower() in self.voice.speech.lower():
            maxStop = np.amax(self.voice.QStop)
            self.totalScore = self.totalScore + self.voice.QStop[maxStop]
            print(str(self.totalScore))

    def startLoop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeThread(self):
        newLoop = asyncio.new_event_loop()
        t = Thread(target=self.startLoop, args=(newLoop,), daemon=True)
        t.start()
        newLoop.call_soon_threadsafe(self.voice.voiceComms)
        return t

    def findCurrentState(self):
        currentState = randint(0,3)
        return currentState

    def nextAction(self):
        self.lift.nextAction()

    def nextActionMax(self,currentState):
        self.lift.nextActionMax(currentState)

    def currentStateEvaluation(self):
        currentState =  self.findCurrentState()
        if currentState != None:
            self.nextAction()
            super().update(currentState, nextActionIndex, self.gamma)
        else:
            print("This is the wrong one")
        print("THIS IS Q " + str(self.Q))
        time.sleep(5)

    def currentStateEvaluationTest(self):
        currentState =  self.findCurrentState()
        if currentState != None:
            self.nextActionMax(currentState)
            self.totalScore = self.totalScore + self.Q[currentState][self.maxAction]
            print(str(self.totalScore))
            print("This is the basic Q Matrix " + str(self.Q))
        else:
            print("No points mate")
        time.sleep(5)

    def trainCozmo(self):
        self.makeThread()
        # robot.say_text("I'm learning how to act when i'm turned").wait_for_completed()
        for i in range (2):
             self.speechCheck()
             self.currentStateEvaluation()
             self.voice.speech = ""
        #self.raiseException()

    def testCozmo(self):
        # robot.say_text("I'm testing how to act when i'm turned").wait_for_completed()
        for i in range (1):
             self.speechCheckTest()
             self.currentStateEvaluationTest()
             self.voice.speech = ""



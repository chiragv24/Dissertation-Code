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
from microIntegration import voiceIntegrationBack

class QLearnSuperClass(abc.ABC):

    nextActionIndex = 0

    def __init__(self):
        self.initState = 0
        self.gamma = 0.5
        self.nextActIndex = 0
        self.Q = []
        self.states = []
        self.rewards = []
        self.rate = 0.05
        self.voice = voiceIntegrationBack()

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
        self.Q = [[0 ,0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0]]
        self.facialQ = [0,0]
        self.states = [0,1,2]
        self.gamma = 0.5
        self.initState = 0
        self.nextActIndex = 0
        self.voice = voiceIntegrationBack()
        self.loop = asyncio.get_event_loop()
        self.maxAction = 0
        self.totalScore = 0
        self.rate = 0.05
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
        self.maxAction = np.where(self.Q[currentState][:] == np.max(self.Q[currentState][:]))
        print(self.Q[currentState][:])
        print(self.maxAction)
        self.maxAction = np.amax(self.maxAction[0])
        facialExp = self.facialExpressionEstimate()
        return self.maxAction

    def writeToFileTest(self,epochNum):
        file = open("testdata" + str(epochNum) + "rate" + str(self.rate)+".txt" , mode='a')
        file.write(str(epochNum) + " " + str(self.rate) + " " + str(self.totalScore))
        file.write("\n")
        file.close()

    def writeToFileTrain(self, currentState, action, reward, epochNum):
        file = open('trainData.txt' + str(epochNum) + "rate" + str(self.rate)+".txt"  , mode='a')
        file.write(str(currentState) + " " + str(action) + " " + str(reward))
        file.write("\n")
        file.close()

    def trainCozmo(self,backVoice):
        epochNum = [5, 10, 25, 50, 100]
        for epoch in range (len(epochNum)):
            open('trainData.txt', mode='w')
            for i in range(epochNum[epoch]):
                if "Move".lower() in backVoice.speech.lower() or "Stop".lower() in backVoice.speech.lower():
                    print("Speech " + backVoice.speech.lower())
                    self.speechCheck(backVoice)
                else:
                    currentState = self.findCurrentState()
                    stringState = ""
                    if currentState == 0:
                        stringState = "Far"
                    elif currentState == 1:
                        stringState = "Optimal"
                    else:
                        stringState = "Close"
                    maxValue = np.max(self.Q[currentState][:])
                    self.nextAction(currentState)
                    nextActStr = ""
                    if nextActionIndex == 0:
                        nextActStr = "Back"
                    elif nextActionIndex == 1:
                        nextActStr = "Front"
                    elif nextActionIndex == 2:
                        nextActStr = "Greet"
                    else:
                        nextActStr = "Idle"
                    reward = 0
                    print("This is the state " + stringState )
                    print("This is the action " + nextActStr)
                    x = input("Please rate the move\n")
                    if x == 'g':
                        bef = self.Q[currentState][nextActionIndex]
                        self.Q[currentState][nextActionIndex] = (1 - self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * round(3 + self.gamma * maxValue))
                        reward = self.Q[currentState][nextActionIndex] - bef
                    if x == 'm':
                        bef = self.Q[currentState][nextActionIndex]
                        self.Q[currentState][nextActionIndex] = (1 - self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * round(self.gamma * maxValue))
                        reward = self.Q[currentState][nextActionIndex] - bef
                    if x == 'b':
                        bef = self.Q[currentState][nextActionIndex]
                        self.Q[currentState][nextActionIndex] = (1 - self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * round(-3 + self.gamma * maxValue))
                        reward = self.Q[currentState][nextActionIndex] - bef
                    print("This is the basic Q Matrix " + str(self.Q))
                    self.writeToFileTrain(currentState, nextActionIndex, reward, epoch)
                print(str(i) + "finished")
                time.sleep(7)
            self.testCozmo(backVoice)
            open("testdata" + str(epochNum[epoch]) + "rate" + str(self.rate) , mode='w')
            self.writeToFileTest(str(epochNum[epoch]))
            self.totalScore = 0
            self.Q = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

    def testCozmo(self,voice):
        print("THIS IS THE TESTING STAGE")
        for i in range (50):
            if "Move".lower() in voice.speech.lower() or "Stop".lower() in voice.speech.lower():
                print("RUNNING VOICE STUFF")
                self.speechCheckTest(voice)
                voice.speech = ""
            else:
                currentState =  self.findCurrentState()
                if currentState != None:
                    self.nextActionMax(currentState)
                    self.totalScore = self.totalScore + self.Q[currentState][self.maxAction]
                    print("This is the basic Q Matrix " + str(self.Q))
                    print(str(self.totalScore))
                else:
                    print("Sorry not found this time bad score")
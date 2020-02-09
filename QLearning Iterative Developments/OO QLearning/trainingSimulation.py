import cozmo
import asyncio
from cozmo.util import distance_mm, speed_mmps
from random import randint
import numpy as np
import time
import abc
import threading
from threading import Thread
import re
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
        self.rate = 0.4
        self.voice.sleepTime = 20
        #self.name = "voice"

    def speechCheck(self,voice,epoch):
        print("This is the voice speech " + voice.speech)
        compMove = re.search(r"ove\b", voice.speech)
        compStop = re.search(r"top\b", voice.speech)
        reward = 0
        dist = self.findCurrentState()
        if compMove:
            print("It is doing the voice methods now")
            randomAction = randint(0,3)
            maxValue = np.max(voice.QMove[dist][:])
            x = self.scoreMove(dist,randomAction)
            if x == 'g':
                bef = voice.QMove[dist][randomAction]
                voice.QMove[dist][randomAction] = (1 - self.rate) * voice.QMove[dist][randomAction] + (self.rate * round(3 + self.gamma * maxValue))
                reward = voice.QMove[dist][nextActionIndex] - bef
            if x == 'm':
                bef = voice.QMove[dist][randomAction]
                voice.QMove[dist][randomAction] = (1 - self.rate) * voice.QMove[dist][randomAction] + (self.rate * round(self.gamma * maxValue))
                reward = voice.QMove[dist][nextActionIndex] - bef
            if x == 'b':
                bef = voice.QMove[dist][randomAction]
                voice.QMove[dist][randomAction] = (1 - self.rate) * voice.QMove[dist][randomAction] + (self.rate * round(-3 + self.gamma * maxValue))
                reward = voice.QMove[dist][nextActionIndex] - bef
            print("This is the move Q Matrix " + str(voice.QMove))
            voice.speech = ""
            self.writeToFileTrain(dist, nextActionIndex, reward, epoch)
        elif compStop:
            print("It is doing the voice methods now")
            randomAction = randint(0, 1)
            maxValue = np.max(voice.QStop)
            if randomAction == 1:
                bef = voice.QStop[randomAction]
                voice.QStop[randomAction] = (1 - self.rate) * voice.QStop[randomAction] + (self.rate * round(3 + self.gamma * maxValue))
                reward = voice.QStop[randomAction]-bef
            else:
                bef = voice.QStop[randomAction]
                voice.QStop[randomAction] = (1 - self.rate) * voice.QStop[randomAction] + (self.rate * round(-3 + self.gamma * maxValue))
                reward = voice.QStop[randomAction]-bef
            print("This is the stop Q Matrix " + str(voice.QStop))
            voice.speech  = ""
            self.writeToFileTrain(dist, nextActionIndex, reward, epoch)

    def speechCheckTest(self,voice,epochs):
        compMove = re.search(r"ove\b", voice.speech)
        compStop = re.search(r"top\b", voice.speech)
        print("This is the voice speech " + voice.speech)
        if compMove:
            dist = self.findCurrentState()
            self.maxAction = np.where(voice.QMove[dist][:] == np.max(self.Q[dist][:]))
            self.maxAction = np.amax(self.maxAction[0])
            scoreBef = self.totalScore
            self.totalScore = self.totalScore + voice.QMove[dist][self.maxAction]
            score = self.totalScore-scoreBef
            self.writeToFileIndTest(score, epochs)
        elif compStop:
            maxStop = np.amax(voice.QStop)
            scoreBef = self.totalScore
            self.totalScore = self.totalScore + maxStop
            score = self.totalScore-scoreBef
            self.writeToFileIndTest(score,epochs)

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
        file = open("testdatafinalscore" + str(epochNum) + "rate" + str(self.rate) + "gamma" + str(self.gamma) +".txt" , mode='a+')
        file.write(str(epochNum) + " " + str(self.rate) + " " + str(self.totalScore))
        file.write("\n")
        file.close()

    def writeToFileIndTest(self,score,epochNum):
        file = open("testdatarate " + str(self.rate) + "epoch" +  str(epochNum)+ "gamma" + str(self.gamma) + ".txt", mode='a+')
        file.write(str(score))
        file.write("\n")
        file.close()

    def writeToFileTrain(self, currentState, action, reward, epochNum):
        file = open('trainData' + str(epochNum) + "rate" + str(self.rate)+ "gamma" + str(self.gamma) + ".txt", mode='a+')
        file.write(str(currentState) + " " + str(action) + " " + str(reward))
        file.write("\n")
        file.close()

    def scoreMove(self,currentState,actionNum):
        if currentState == 0:
            if actionNum == 1:
                return 'g'
            else:
                return 'b'
        elif currentState == 1:
            if actionNum == 2:
                return 'g'
            elif actionNum == 3:
                return 'm'
            else:
                return 'b'
        else:
            if actionNum == 0:
                return 'g'
            else:
                return 'b'

    def trainCozmo(self,backVoice):
        gammaRates = [0.1,0.25,0.5,0.75,1]
        for gamma in range (len(gammaRates)):
            self.gamma = gammaRates[gamma]
            learnRates = [0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,1]
            for learn in range (len(learnRates)):
                self.rate = learnRates[learn]
                epochNum = [5, 10, 25, 50, 100, 150, 200, 250, 300, 350, 400]
                for epoch in range (len(epochNum)):
                    open('trainData.txt', mode='w')
                    for i in range(epochNum[epoch]):
                        compMove = re.search(r"ove\b", backVoice.speech)
                        compStop = re.search(r"top\b", backVoice.speech)
                        if compMove or compStop:
                            print("Speech " + backVoice.speech.lower())
                            self.speechCheck(backVoice,epoch)
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
                            x = self.scoreMove(currentState,nextActionIndex)
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
                    self.testCozmo(backVoice,str(epochNum[epoch]))
                    self.writeToFileTest(str(epochNum[epoch]))
                    self.totalScore = 0
                    self.Q = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
                    backVoice.QMove = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
                    backVoice.QStop = [0,0]

    def testCozmo(self,voice,epochs):
        print("THIS IS THE TESTING STAGE")
        for i in range (50):
            compMove = re.search(r"ove\b", voice.speech)
            compStop = re.search(r"top\b", voice.speech)
            if compMove or compStop:
                print("RUNNING VOICE STUFF")
                self.speechCheckTest(voice,epochs)
                voice.speech = ""
                print(str(self.totalScore))
            else:
                currentState =  self.findCurrentState()
                if currentState != None:
                    self.nextActionMax(currentState)
                    scoreBef = self.totalScore
                    self.totalScore = self.totalScore + self.Q[currentState][self.maxAction]
                    moveScore = self.totalScore - scoreBef
                    self.writeToFileIndTest(moveScore,epochs)
                    print("This is the basic Q Matrix " + str(self.Q))
                    print(str(self.totalScore))
                else:
                    print("Sorry not found this time bad score")
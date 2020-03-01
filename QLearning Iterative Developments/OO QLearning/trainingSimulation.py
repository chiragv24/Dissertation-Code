import asyncio
from random import randint
import numpy as np
import abc
from threading import Thread
import re
from microIntegration import voiceIntegrationBack

class QLearnDistOrthogonal():

    nextActionIndex = 0

    def __init__(self):
        self.actions = [0,1,2,3]
        self.Q = [[0 ,0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0]]
        self.states = [0,1,2]
        self.nextActIndex = 0
        self.voice = voiceIntegrationBack()
        self.maxAction = 0
        self.totalScore = 0
        self.gamma = 0.5
        self.nextActIndex = 0
        self.loop = asyncio.get_event_loop()
        self.rate = 0.4

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
        return self.maxAction

    def writeToFileTestEpoch(self,epochNum):
        file = open("testdatafinalscore"+"epoch"+str(epochNum)+".txt",mode='a+')
        fileName = file.name
        file.write(str(epochNum) + " " + str(self.rate) + " " + str(self.totalScore))
        file.write("\n")
        file.close()
        return fileName

    def writeToFileTestRate(self,epochNum):
        file = open("testdatafinalscore"+"rate"+str(self.rate)+".txt",mode='a+')
        fileName = file.name
        file.write(str(epochNum) + " " + str(self.rate) + " " + str(self.totalScore))
        file.write("\n")
        file.close()
        return fileName

    def writeToFileIndTest(self,score,epochNum):
        file = open("testdatarate " + str(self.rate) + "epoch" +  str(epochNum)+ "gamma" + str(self.gamma) + ".txt", mode='a+')
        file.write(str(score))
        file.write("\n")
        file.close()

    def writeToFileTrain(self, currentState, action, reward, epochNum, quality):
        file = open('trainData' + str(epochNum) + "rate" + str(self.rate)+ "gamma" + str(self.gamma) + ".txt", mode='a+')
        file.write(str(currentState) + " " + str(action) + " " + str(reward) + " " +  str(quality))
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
        gammaRates = [0.9]
        quality = 0
        for gamma in range (len(gammaRates)):
            #learnRates = [0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,1]
            self.gamma = gammaRates[gamma]
            learnRates = [0.4]
            for learn in range (len(learnRates)):
                self.rate = learnRates[learn]
                epochNum = [4000]
                for epoch in range (len(epochNum)):
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
                                #bef = self.Q[currentState][nextActionIndex]
                                self.Q[currentState][nextActionIndex] = (1 - self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * (3 + self.gamma * maxValue))
                                reward = self.Q[currentState][nextActionIndex]
                                quality = 3
                            if x == 'm':
                                #bef = self.Q[currentState][nextActionIndex]
                                self.Q[currentState][nextActionIndex] = (1 - self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * (self.gamma * maxValue))
                                reward = self.Q[currentState][nextActionIndex]
                                quality = 0
                            if x == 'b':
                                #bef = self.Q[currentState][nextActionIndex]
                                self.Q[currentState][nextActionIndex] = (1 - self.rate) * self.Q[currentState][nextActionIndex] + (self.rate * (-3 + self.gamma * maxValue))
                                reward = self.Q[currentState][nextActionIndex]
                                quality = -3
                            print("This is the basic Q Matrix " + str(self.Q))
                            self.writeToFileTrain(currentState, nextActionIndex, reward, epoch, quality)
                        print(str(i) + "finished")
                    self.testCozmo(backVoice,str(epochNum[epoch]))
                    self.writeToFileTestRate(str(epochNum[epoch]))
                    self.writeToFileTestEpoch(str(epochNum[epoch]))
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
                    self.totalScore = round(self.totalScore + self.Q[currentState][self.maxAction],2)
                    moveScore = self.totalScore - scoreBef
                    self.writeToFileIndTest(moveScore,epochs)
                    print("This is the basic Q Matrix " + str(self.Q))
                    print(str(self.totalScore))
                else:
                    print("Sorry not found this time bad score")
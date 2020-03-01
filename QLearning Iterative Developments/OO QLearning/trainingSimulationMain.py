from trainingSimulation import QLearnDistOrthogonal
from microIntegration import voiceIntegrationBack
import asyncio
from threading import Thread

class trainMain():

    def __init__(self):
        self.agent1 = QLearnDistOrthogonal()
        self.voice = voiceIntegrationBack()

    def startLoop(self,loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeThread(self):
        newLoop = asyncio.new_event_loop()
        t = Thread(target=self.startLoop, args=(newLoop,), daemon=True)
        t.start()
        newLoop.call_soon_threadsafe(self.voice.voiceComms)
        return t

    def runTrain(self):
        self.agent1.trainCozmo(self.voice)


train = trainMain()
train.makeThread()
train.runTrain()





from interactiveCodeDist import QLearnDistOrthogonal
from interactiveCode import QLearnLiftOrthogonal
from interactiveCode import QLearnTurnOrthogonal
from threading import Thread
import threading
import asyncio
import cozmo
import time
from microIntegrationInteractive import voiceIntegration
from microIntegration import voiceIntegrationBack


class mainWorker():

    def __init__(self):
        self.voice = voiceIntegration()
        self.backVoice = voiceIntegrationBack()
        self.agent1 = QLearnDistOrthogonal()

    def startWLoop(self,loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeWorker(self):
        #newLoopWorker = asyncio.new_event_loop()
        tWorker = Thread(target=self.runTrain1)
        tWorker.start()
        #newLoopWorker.call_soon_threadsafe(self.runTrain1)
        return tWorker

    def startLoop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeThread(self):
        newLoopListener = asyncio.new_event_loop()
        tListener = Thread(target=self.startLoop, args=(newLoopListener,), daemon=True)
        tListener.start()
        newLoopListener.call_soon_threadsafe(self.backVoice.voiceComms)
        return tListener

    def runTrain1(self):
        cozmo.run_program(self.cozmoDistHelper)

    async def cozmoDistHelper(self,robot:cozmo.robot.Robot):
        await self.agent1.trainCozmo(robot,self.voice,self.backVoice)

    async def runLoop(self,robot:cozmo.robot.Robot):
        while True:
            await self.agent1.testCozmo(robot,self.backVoice)


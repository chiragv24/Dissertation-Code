
# from testingMultiProcessOrthog import QLearnDistOrthogonal
# from testingMultiProcessOrthog import QLearnTurnOrthogonal
# from testingMultiProcessOrthog import QLearnLiftOrthogonal

from CleanerNewOrthogonals import QLearnDistOrthogonal
from CleanerNewOrthogonals import QLearnLiftOrthogonal
from CleanerNewOrthogonals import QLearnTurnOrthogonal
from threading import Thread
import threading
from microIntegration import voiceIntegrationBack

import cozmo
import asyncio
import time
from cozmo.util import degrees

class main:

    def __init__(self):
        self.agent1 = QLearnDistOrthogonal()
        self.agent2 = QLearnLiftOrthogonal()
        self.voice = voiceIntegrationBack()
        self.agent3 = QLearnTurnOrthogonal()

    def cozmoDist(self):
        cozmo.run_program(self.cozmoDistHelper)

    async def cozmoDistHelper(self,robot:cozmo.robot.Robot):
         await self.agent1.trainCozmo(robot,self.voice)

    def cozmoLift(self):
        cozmo.run_program(self.cozmoLiftHelper)

    async def cozmoLiftHelper(self,robot:cozmo.robot.Robot):
         await self.agent2.trainCozmo(robot,self.voice)

    def cozmoTurn(self):
        cozmo.run_program(self.cozmoTurnHelper)

    async def cozmoTurnHelper(self,robot:cozmo.robot.Robot):
         await self.agent3.trainCozmo(robot,self.voice)

    def startLoop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeThread(self):
        newLoop = asyncio.new_event_loop()
        t = Thread(target=self.startLoop,args=(newLoop,),daemon=True)
        t.start()
        newLoop.call_soon_threadsafe(self.voice.voiceComms)
        return t

    async def runLoop(self,robot: cozmo.robot.Robot):
        angle = str(robot.pose_pitch.degrees)
        await robot.say_text("I'm going to test myself now").wait_for_completed()
        while True:
            if robot.is_picked_up:
                await self.agent2.testCozmo(robot,self.voice)
            elif 90 < float(angle) < 180:
                await self.agent3.testCozmo(robot,self.voice)
            else:
                await self.agent1.testCozmo(robot,self.voice)
            time.sleep(5)


runner = main()
runner.makeThread()
# #Training sessions
runner.cozmoDist()
runner.cozmoLift()
runner.cozmoTurn()
loop = asyncio.get_event_loop()
loop.call_soon_threadsafe(cozmo.run_program(runner.runLoop))











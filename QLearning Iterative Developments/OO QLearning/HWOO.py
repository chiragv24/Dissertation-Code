
# from testingMultiProcessOrthog import QLearnDistOrthogonal
# from testingMultiProcessOrthog import QLearnTurnOrthogonal
# from testingMultiProcessOrthog import QLearnLiftOrthogonal

from CleanerNewOrthogonals import QLearnDistOrthogonal
from CleanerNewOrthogonals import QLearnLiftOrthogonal
from CleanerNewOrthogonals import QLearnTurnOrthogonal
from threading import Thread
from microIntegration import voiceIntegration
from multiprocessing import Process

import cozmo
import asyncio
import time
from cozmo.util import degrees

class main:

    def __init__(self):
        self.agent1 = QLearnDistOrthogonal()
        self.agent2 = QLearnLiftOrthogonal()
        self.voice = voiceIntegration()
        self.agent3 = QLearnTurnOrthogonal()

    def cozmoDist(self):
        cozmo.run_program(self.agent1.trainCozmo)

    def cozmoLift(self):
        cozmo.run_program(self.agent2.trainCozmo)

    def cozmoTurn(self):
        cozmo.run_program(self.agent3.trainCozmo)

    def startLoop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def makeProcess(self):
        newLoop = asyncio.new_event_loop()
        p = Process(target=self.startLoop,args=(newLoop,))
        p.daemon = True
        p.start()
        newLoop.call_soon_threadsafe(self.voice.voiceComms)
        return p


    async def runLoop(self,robot: cozmo.robot.Robot):
        angle = str(robot.pose_pitch.degrees)
        self.makeProcess()
        while True:
            if robot.is_picked_up:
                await self.agent2.testCozmo(robot)
            elif 90 < float(angle) < 180:
                await self.agent3.testCozmo(robot)
            else:
                await self.agent1.testCozmo(robot)
            time.sleep(2)


runner = main()
#Training sessions
runner.cozmoDist()
runner.cozmoLift()
runner.cozmoTurn()

loop = asyncio.get_event_loop()
loop.call_soon_threadsafe(cozmo.run_program(runner.runLoop))











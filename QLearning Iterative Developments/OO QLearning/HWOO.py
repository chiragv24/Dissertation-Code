
from CleanerNewOrthogonals import QLearnDistOrthogonal
from CleanerNewOrthogonals import QLearnLiftOrthogonal
from CleanerNewOrthogonals import QLearnTurnOrthogonal
import cozmo
import asyncio
from cozmo.util import degrees

class main:

    def __init__(self):
        self.agent1 = QLearnDistOrthogonal()
        self.agent2 = QLearnLiftOrthogonal()
        self.agent3 = QLearnTurnOrthogonal()

    def cozmoDist(self):
        cozmo.run_program(self.agent1.trainCozmo)

    def cozmoLift(self):
        cozmo.run_program(self.agent2.trainCozmo)

    def cozmoTurn(self):
        cozmo.run_program(self.agent3.trainCozmo)

    async def runLoop(self,robot: cozmo.robot.Robot):
        angle = str(robot.pose_pitch.degrees)
        while True:
            if robot.is_picked_up:
                await self.agent2.testCozmo(robot)
            elif 90 < float(angle) < 180:
                await self.agent3.testCozmo(robot)
            else:
                await self.agent1.testCozmo(robot)


runner = main()
#Training sessions
runner.cozmoDist()
runner.cozmoLift()
runner.cozmoTurn()

loop = asyncio.get_event_loop()
loop.call_soon_threadsafe(cozmo.run_program(runner.runLoop))



# cozmo.run_program(agent1.testCozmo)
#cozmo.run_program(agent3.testCozmo)










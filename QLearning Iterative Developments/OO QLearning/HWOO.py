# from OrthogonalAsyncTesting import QLearnDistOrthogonal
# #from OrthogonalAsyncTesting import QLearnGreetOrthogonal
# from OrthogonalAsyncTesting import QLearnLiftOrthogonal
# from OrthogonalAsyncTesting import QLearnTurnOrthogonal
from CleanerNewOrthogonals import QLearnDistOrthogonal
from CleanerNewOrthogonals import QLearnLiftOrthogonal
from CleanerNewOrthogonals import QLearnTurnOrthogonal
import cozmo
import asyncio
from cozmo.util import degrees


agent1 = QLearnDistOrthogonal()
agent2 = QLearnLiftOrthogonal()
agent3 = QLearnTurnOrthogonal()

def cozmoDist():
    cozmo.run_program(agent1.trainCozmo)

def cozmoLift():
    cozmo.run_program(agent2.trainCozmo)

def cozmoTurn():
    cozmo.run_program(agent3.trainCozmo)


#Training sessions
cozmoDist()
cozmoLift()
cozmoTurn()

async def runLoop(robot:cozmo.robot.Robot):
    angle = str(robot.pose_pitch.degrees)
    while True:
        if robot.is_picked_up:
            await agent2.testCozmo(robot)
        elif 90 < float(angle) < 180:
            await agent3.testCozmo(robot)
        else:
            await agent1.testCozmo(robot)

loop = asyncio.get_event_loop()
loop.call_soon_threadsafe(cozmo.run_program(runLoop))



# cozmo.run_program(agent1.testCozmo)
#cozmo.run_program(agent3.testCozmo)










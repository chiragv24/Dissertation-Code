from interactiveCode import QLearnDistOrthogonal
from CleanerNewOrthogonals import QLearnLiftOrthogonal
from CleanerNewOrthogonals import QLearnTurnOrthogonal
from threading import Thread
import threading
import cozmo
from microIntegrationInteractive import voiceIntegration

class main:

    def __init__(self):
        self.agent1 = QLearnDistOrthogonal()
        self.voice = voiceIntegration()

    def runTrain1(self):
        cozmo.run_program(self.cozmoDistHelper)

    async def cozmoDistHelper(self,robot:cozmo.robot.Robot):
         await self.agent1.trainCozmo(robot,self.voice)

m = main()
m.runTrain1()
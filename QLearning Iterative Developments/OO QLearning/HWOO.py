
from asyncioTesting import QLearnDistOrthogonal
from asyncioTesting import QLearnGreetOrthogonal
from asyncioTesting import QLearnLiftOrthogonal
from asyncioTesting import QLearnTurnOrthogonal
from microIntegration import voiceIntegration
import cozmo
agent1 = QLearnDistOrthogonal()
agent2 = QLearnGreetOrthogonal()
agent3 = QLearnLiftOrthogonal()
agent4 = QLearnTurnOrthogonal()
agent5 = voiceIntegration()

def cozmoDist():
    cozmo.run_program(agent1.trainCozmo)

def cozmoGreet():
    cozmo.run_program(agent2.trainCozmo)

def cozmoLift():
    cozmo.run_program(agent3.trainCozmo)

def cozmoTurn():
    cozmo.run_program(agent4.trainCozmo)

#cozmoDist()
#cozmoGreet()
cozmoLift()
##cozmoTurn()








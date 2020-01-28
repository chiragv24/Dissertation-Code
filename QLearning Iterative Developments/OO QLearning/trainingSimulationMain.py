from trainingSimulation import QLearnDistOrthogonal
from trainingSimulation import QLearnLiftOrthogonal
from trainingSimulation import QLearnTurnOrthogonal
from microIntegration import voiceIntegration
from random import randint
import asyncio
import threading
from threading import Thread
import time

agent1 = QLearnDistOrthogonal()
agent2 = QLearnLiftOrthogonal()
voice = voiceIntegration()
agent3 = QLearnTurnOrthogonal()


def startLoop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def makeThread():
    newLoop = asyncio.new_event_loop()
    t = Thread(target=startLoop, args=(newLoop,), daemon=True)
    t.start()
    newLoop.call_soon_threadsafe(voice.voiceComms)
    return t

makeThread()

agent1.trainCozmo(voice)
agent2.trainCozmo(voice)
#agent3.trainCozmo()

for i in range (10):
    print("Testing loop " + str(i) )
    orthog = randint(0,2)
    print("Chosen one " + str(orthog))
    if orthog == 0:
        agent1.testCozmo(voice)
    elif orthog == 1:
        agent2.testCozmo(voice)
    else:
        print("Not this time")
        #agent3.testCozmo()
    time.sleep(5)


print(agent1.Q)
print(agent2.Q)
print(agent3.Q)
print(agent1.totalScore)
print(agent2.totalScore)
print(agent3.totalScore)



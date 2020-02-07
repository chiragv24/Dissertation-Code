from trainingSimulation import QLearnDistOrthogonal
from microIntegration import voiceIntegrationBack
from random import randint
import asyncio
import threading
from threading import Thread
import time

agent1 = QLearnDistOrthogonal()
voice = voiceIntegrationBack()

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

print(agent1.Q)
print(agent1.totalScore)




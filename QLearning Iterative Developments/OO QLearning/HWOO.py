from QLearnSuperClass import QLearnDistOrthogonal
from QLearnSuperClass import QLearnTurnOrthogonal
from QLearnSuperClass import QLearnLiftOrthogonal
from QLearnSuperClass import QLearnGreetOrthogonal
from microIntegration import voiceIntegration
import cozmo
import threading
agent1 = QLearnDistOrthogonal()
agent5 = voiceIntegration()
import logging
import asyncio

loop = asyncio.get_event_loop()

def ag1():
    cozmo.run_program(agent1.trainCozmo)

def voiceRecog():
    agent5.voiceComms(loop)

distOrthog = threading.Thread(name="dist",target=ag1)
listenerThread = threading.Thread(name="dist",target=voiceRecog,daemon=True)

if __name__=='__main__':
    distOrthog.start()
    listenerThread.start()
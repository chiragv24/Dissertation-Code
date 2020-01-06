import cozmo
from cozmo.util import distance_mm
import threading
#from QLearnSuperClass import QLearnDistOrthogonal
from QLearnSuperClass import QLearnTurnOrthogonal
from QLearnSuperClass import QLearnLiftOrthogonal
from QLearnSuperClass import QLearnGreetOrthogonal
from microIntegration import voiceRecognition
from asyncioTesting import QLearnDistOrthogonal
import multiprocessing
from multiprocessing import Process
import time


agent1 = QLearnDistOrthogonal()
agent2 = QLearnTurnOrthogonal()
agent3 = QLearnGreetOrthogonal()
agent4 = QLearnLiftOrthogonal()
agent5 = voiceRecognition()

#cozmo.run_program(agent1.trainCozmo,use_viewer=True)

def ag1():
    cozmo.run_program(agent1.trainCozmo)

async def ag2():
    await cozmo.run_program(agent2.trainCozmo)

async def ag3():
    await cozmo.run_program(agent3.trainCozmo)

async def ag4():
    await cozmo.run_program(agent4.trainCozmo)

async def ag5():
    await cozmo.run_program(agent5.voiceCommsAction)

if __name__=='__main__':
    ag1()
    # ag2()
    # ag3()
    # ag4()









    # distOrthog = Process(target=ag1)
    # turnOrthog = Process(target=ag2)
    # greetOrthog = Process(target=ag3)
    # liftOrthog = Process(target=ag4)
    # listenerThread = Process(target = ag5)

    # distOrthog = threading.Thread(name="dist",target=ag1)
    # turnOrthog = threading.Thread(name="turn",target=ag2)
    # greetOrthog = threading.Thread(name="greet",target=ag3)
    # liftOrthog = threading.Thread(name="lift",target=ag4)
    # listenerThread = threading.Thread(name="voice",target = ag5,daemon=True)

    #JOIN MEANS WAIT FOR THREAD TO FINISH

    # listenerThread.start()
    # distOrthog.start()
    # distOrthog.join()
    # turnOrthog.start()
    # turnOrthog.join()
    # greetOrthog.start()
    # greetOrthog.join()
    # liftOrthog.start()
    # liftOrthog.join()

    # distOrthog.start()
    # turnOrthog.daemon = True
    # turnOrthog.start()
    # greetOrthog.daemon = True
    # greetOrthog.start()
    # liftOrthog.daemon = True
    # liftOrthog.start()
    # turnOrthog.join()
    # greetOrthog.join()
    # liftOrthog.join()






    #listenerThread.start()

#     #START ANOTHER THREAD WHICH WIL CALL THE LISTENER THREAD METHOD
#     #IF THERE IS RECOGNIZED COMMAND FROM IN THE OTHER FUNCTION THEN STOP ALL 4 OF THESE
#     #SEQUENTIALLY RUN THE OTHER ONE AND THEN RESUME THIS THREAD
#     #KILL AND RESTART THAT THREAD / KEEP IT IDLE

# def method1():
#     for i in range (1000):
#         print("Hello how are you doing today")
#
# def method2():
#     m = 0
#     for i in range (100):
#         m = m + 1
#         print(m)
#
#
# if __name__=='__main__':
#     #x = print hello ... 1000 times
#     #y = print 1 to 100
#
#     x = Process(target=method1)
#     y = Process(target=method2)
#     x.start()
#     y.start()
#     x.join()
#     y.join()

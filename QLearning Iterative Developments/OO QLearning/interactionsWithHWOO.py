import cozmo
from cozmo.util import distance_mm
from QLearnSuperClass import QLearnDistOrthogonal
from QLearnSuperClass import QLearnTurnOrthogonal
from QLearnSuperClass import QLearnLiftOrthogonal
from QLearnSuperClass import QLearnGreetOrthogonal
import multiprocessing
from multiprocessing import Process
import time
#from microIntegration import voiceComms

#
# agent1 = QLearnDistOrthogonal()
# agent2 = QLearnTurnOrthogonal()
# agent3 = QLearnGreetOrthogonal()
# agent4 = QLearnLiftOrthogonal()
#
# #cozmo.run_program(agent1.trainCozmo,use_viewer=True)
#
# def ag1():
#     cozmo.run_program(agent1.trainCozmo,use_viewer=True)
#
# def ag2():
#     cozmo.run_program(agent2.trainCozmo)
#
# def ag3():
#     cozmo.run_program(agent3.trainCozmo)
#
# def ag4():
#     cozmo.run_program(agent4.trainCozmo)
#
# if __name__=='__main__':
#     distOrthog = Process(target=ag1)
#     turnOrthog = Process(target=ag2)
#     greetOrthog = Process(target=ag3)
#     liftOrthog = Process(target=ag4)
#     #listenerThread = Process(target = voiceComms)
#
#     distOrthog.start()
#     time.sleep(30)
#     turnOrthog.daemon = True
#     turnOrthog.start()
#     time.sleep(30)
#     greetOrthog.daemon = True
#     greetOrthog.start()
#     time.sleep(30)
#     liftOrthog.daemon = True
#     liftOrthog.start()
#     time.sleep(30)
#     print(agent1.Q)
#     print(agent2.Q)
#     print(agent3.Q)
#     print(agent4.Q)
    # turnOrthog.join()
    # greetOrthog.join()
    # liftOrthog.join()

    #listenerThread.start()

#     #START ANOTHER THREAD WHICH WIL CALL THE LISTENER THREAD METHOD
#     #IF THERE IS RECOGNIZED COMMAND FROM IN THE OTHER FUNCTION THEN STOP ALL 4 OF THESE
#     #SEQUENTIALLY RUN THE OTHER ONE AND THEN RESUME THIS THREAD
#     #KILL AND RESTART THAT THREAD / KEEP IT IDLE

def method1():
    for i in range (10):
        print("Hello how are you doing today")

def method2():
    m = 0
    for i in range (100):
        m = m + 1
        print(m)


if __name__=='__main__':
    #In this case the 1st method is quicker
    #the second is slower

    x = Process(target=method1)
    y = Process(target=method2)
    y.start()
    x.start()
    y.join()
    x.join()

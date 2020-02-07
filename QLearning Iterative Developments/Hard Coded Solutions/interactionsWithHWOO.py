# import cozmo
# from cozmo.util import distance_mm
# import threading
# #from QLearnSuperClass import QLearnDistOrthogonal
# # from QLearnSuperClass import QLearnTurnOrthogonal
# # from QLearnSuperClass import QLearnLiftOrthogonal
# # from QLearnSuperClass import QLearnGreetOrthogonal
# from microIntegration import voiceIntegration
# from asyncioTesting import QLearnDistOrthogonal
# from asyncioTesting import QLearnGreetOrthogonal
# import asyncio
# # from asyncioTesting import QLearnGreetOrthogonal
#
#
# import multiprocessing
# from multiprocessing import Process
# import time
#
#
# agent1 = QLearnDistOrthogonal()
# agent2 = QLearnGreetOrthogonal()
# #agent3 = QLearnTurnOrthogonal()
# #agent4 = QLearnLiftOrthogonal()
# agent5 = voiceIntegration()
#
# #cozmo.run_program(agent1.trainCozmo,use_viewer=True)
#
# # async def loop1():
# #     await ag1()
# #     #await ag2()
# #     # await ag3()
# #     # await ag4()
# #
# # async def loop2():
# #     await ag5()
#
#
# def ag1():
#     cozmo.run_program(agent1.trainCozmo)
#
# def ag2():
#     cozmo.run_program(agent2.trainCozmo)
#
# # async def ag2():
# #     await cozmo.run_program(agent2.trainCozmo)
# #
# # def ag3():
# #      cozmo.run_program(agent3.trainCozmo)
# # #
# # def ag4():
# #      cozmo.run_program(agent4.trainCozmo)
# #
# def ag5():
#     print("Thread acqu")
#     threadLock.acquire()
#     cozmo.run_program(agent5.voiceCommsAction)
#     threadLock.release()
#     print("Thread unlock")
#
# # def launch_event_loop1():
# #     loop = asyncio.new_event_loop()
# #     loop.run_until_complete(loop1())
# #
# # def launch_event_loop2():
# #     loop = asyncio.new_event_loop()
# #     loop.run_until_complete(loop2())
#
#
# threadLock = threading.Lock()
#
# distOrthog = threading.Thread(name="dist",target=ag1)
# # greetOrthog = threading.Thread(name="greet",target=ag2)
# # turnOrthog = threading.Thread(name="turn",target=ag3)
# # liftOrthog = threading.Thread(name="lift",target=ag4)
# listenerThread = threading.Thread(name="voice",target = ag5)
#
# if __name__=='__main__':
#
#     async def voiceCommsAction(self,robot:cozmo.robot.Robot):
#         asyncio.get_event_loop()
#         while True:
#             speech = self.voiceComms()
#             if self.clearSpeech:
#                 if "Cozmo".lower() in speech.lower() or "Cosmo".lower() in speech.lower():
#                     await robot.say_text("Hello nice to meet you").wait_for_completed()
#
#     distOrthog.start()
#     # # greetOrthog.start()
#     listenerThread.start()
#     # ag1()
#     # ag2()
#     # ag5()
#     #
#     # ag3()
#     # ag4()
#     # while True:
#     #     t1 = threading.Thread(target=launch_event_loop1())
#     #     t2 = threading.Thread(target=launch_event_loop2())
#     #     t1.start()
#     #     t2.start()
#
#
#
#
#
#
#
#
#
#
#     # distOrthog = Process(target=ag1)
#     # turnOrthog = Process(target=ag2)
#     # greetOrthog = Process(target=ag3)
#     # liftOrthog = Process(target=ag4)
#     # listenerThread = Process(target = ag5)
#
#     # distOrthog = threading.Thread(name="dist",target=ag1)
#     # turnOrthog = threading.Thread(name="turn",target=ag2)
#     # greetOrthog = threading.Thread(name="greet",target=ag3)
#     # liftOrthog = threading.Thread(name="lift",target=ag4)
#     # listenerThread = threading.Thread(name="voice",target = ag5,daemon=True)
#
#     #JOIN MEANS WAIT FOR THREAD TO FINISH
#
#     # listenerThread.start()
#     # distOrthog.start()
#     # distOrthog.join()
#     # turnOrthog.start()
#     # turnOrthog.join()
#     # greetOrthog.start()
#     # greetOrthog.join()
#     # liftOrthog.start()
#     # liftOrthog.join()
#
#     # distOrthog.start()
#     # turnOrthog.daemon = True
#     # turnOrthog.start()
#     # greetOrthog.daemon = True
#     # greetOrthog.start()
#     # liftOrthog.daemon = True
#     # liftOrthog.start()
#     # turnOrthog.join()
#     # greetOrthog.join()
#     # liftOrthog.join()
#
#
#
#
#
#
#     #listenerThread.start()
#
# #     #START ANOTHER THREAD WHICH WIL CALL THE LISTENER THREAD METHOD
# #     #IF THERE IS RECOGNIZED COMMAND FROM IN THE OTHER FUNCTION THEN STOP ALL 4 OF THESE
# #     #SEQUENTIALLY RUN THE OTHER ONE AND THEN RESUME THIS THREAD
# #     #KILL AND RESTART THAT THREAD / KEEP IT IDLE
#
# # def method1():
# #     for i in range (1000):
# #         print("Hello how are you doing today")
# #
# # def method2():
# #     m = 0
# #     for i in range (100):
# #         m = m + 1
# #         print(m)
# #
# #
# # if __name__=='__main__':
# #     #x = print hello ... 1000 times
# #     #y = print 1 to 100
# #
# #     x = Process(target=method1)
# #     y = Process(target=method2)
# #     x.start()
# #     y.start()
# #     x.join()
# #     y.join()

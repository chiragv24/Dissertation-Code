# from interactiveCodeDist import QLearnDistOrthogonal
# from interactiveCode import QLearnLiftOrthogonal
# from uiTestingWorkerCode import mainWorker
# from interactiveCode import QLearnTurnOrthogonal
# from threading import Thread
# import threading
# import asyncio
# import cozmo
# import time
# from microIntegrationInteractive import voiceIntegration
# from microIntegration import voiceIntegrationBack

# class main:
#
#     def __init__(self):
#         self.voice = voiceIntegration()
#         self.backVoice = voiceIntegrationBack()


    # def startWLoop(self,loop):
    #     asyncio.set_event_loop(loop)
    #     loop.run_forever()
    #
    # def makeWorker(self):
    #     newLoopWorker = asyncio.new_event_loop()
    #     tWorker = Thread(target=self.startWLoop,args=(newLoopWorker,))
    #     tWorker.start()
    #     newLoopWorker.call_soon_threadsafe(self.runTrain1)
    #     return tWorker

    # def startLoop(self, loop):
    #     asyncio.set_event_loop(loop)
    #     loop.run_forever()
    #
    # def makeThread(self):
    #     newLoopListener = asyncio.new_event_loop()
    #     tListener = Thread(target=self.startLoop,args=(newLoopListener,),daemon=True)
    #     tListener.start()
    #     newLoopListener.call_soon_threadsafe(self.backVoice.voiceComms)
    #     return tListener

    # def runTrain1(self):
    #     cozmo.run_program(self.cozmoDistHelper)
    #
    # def runTrain2(self):
    #     cozmo.run_program(self.cozmoLiftHelper)
    #
    # def runTrain3(self):
    #     cozmo.run_program(self.cozmoTurnHelper)
    #
    # async def cozmoDistHelper(self,robot:cozmo.robot.Robot):
    #     await self.agent1.trainCozmo(robot,self.voice,self.backVoice)
    #
    # async def cozmoLiftHelper(self,robot:cozmo.robot.Robot):
    #     await self.agent2.trainCozmo(robot,self.voice,self.backVoice)
    #
    # async def cozmoTurnHelper(self,robot:cozmo.robot.Robot):
    #     await self.agent3.trainCozmo(robot,self.voice,self.backVoice)
    #
    # async def runLoop(self,robot:cozmo.robot.Robot):
    #     while True:
    #         await self.agent1.testCozmo(robot,self.backVoice)
#
# ui = UI()
# main = mainWorker()
# ui.updateLabels(main.,m.voice,m.agent1.Q)



# m = main()
# # m.makeThread()
# m.runTrain1()
# #m.runTrain1()
# #m.runTrain2()
# loop = asyncio.get_event_loop()
# loop.call_soon_threadsafe(cozmo.run_program(m.runLoop))

#angle = str(robot.pose_pitch.degrees)
# await robot.say_text("I'm going to give you 5 seconds to change").wait_for_completed()
# print("Time to sleep")
# time.sleep(5)
# print("Woken up from sleep")
# if robot.is_picked_up:
#     await self.agent2.testCozmo(robot,self.backVoice)
# elif 90 <= float(angle) <= 180:
#     await self.agent3.testCozmo(robot,self.backVoice)
# else:





# class main:
#
#     def __init__(self):
#         self.agent1 = QLearnDistOrthogonal()
#         self.voice = voiceIntegration()
#         self.backVoice = voiceIntegrationBack()
#         self.agent2 = QLearnLiftOrthogonal()
#         self.agent3 = QLearnTurnOrthogonal()
#
#     def startLoop(self, loop):
#         asyncio.set_event_loop(loop)
#         loop.run_forever()
#
#     def makeThread(self):
#         newLoop = asyncio.new_event_loop()
#         #newLoopUI = asyncio.new_event_loop()
#         t = Thread(target=self.startLoop,args=(newLoop,),daemon=True)
#         #t1 = Thread(target=self.startLoop,args=(newLoopUI,))
#         t.start()
#         #t1.start()
#         newLoop.call_soon_threadsafe(self.backVoice.voiceComms)
#         #newLoopUI.call_soon_threadsafe(self.visual.spawnWindow)
#         return t
#
#     def runTrain1(self):
#         cozmo.run_program(self.cozmoDistHelper)
#
#     def runTrain2(self):
#         cozmo.run_program(self.cozmoLiftHelper)
#
#     def runTrain3(self):
#         cozmo.run_program(self.cozmoTurnHelper)
#
#     async def cozmoDistHelper(self,robot:cozmo.robot.Robot):
#          await self.agent1.trainCozmo(robot,self.voice,self.backVoice)
#
#     async def cozmoLiftHelper(self,robot:cozmo.robot.Robot):
#         await self.agent2.trainCozmo(robot,self.voice,self.backVoice)
#
#     async def cozmoTurnHelper(self,robot:cozmo.robot.Robot):
#         await self.agent3.trainCozmo(robot,self.voice,self.backVoice)
#
#     async def runLoop(self,robot:cozmo.robot.Robot):
#         angle = str(robot.pose_pitch.degrees)
#         while True:
#             # await robot.say_text("I'm going to give you 5 seconds to change").wait_for_completed()
#             # print("Time to sleep")
#             # time.sleep(5)
#             # print("Woken up from sleep")
#             # if robot.is_picked_up:
#             #     await self.agent2.testCozmo(robot,self.backVoice)
#             # elif 90 <= float(angle) <= 180:
#             #     await self.agent3.testCozmo(robot,self.backVoice)
#             # else:
#             await self.agent1.testCozmo(robot,self.backVoice)
#
# m = main()
# m.makeThread()
# m.runTrain1()
# #m.runTrain1()
# #m.runTrain2()
# loop = asyncio.get_event_loop()
# loop.call_soon_threadsafe(cozmo.run_program(m.runLoop))
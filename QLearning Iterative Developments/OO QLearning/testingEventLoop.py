# import cozmo
# import logging
# from cozmo.util import distance_mm, speed_mmps
# import asyncio
#
# loop = asyncio.get_event_loop()
#
# def voiceAction(robot:cozmo.robot.Robot):
#     robot.say_text("Hello how are you today").wait_for_completed()
#     robot.loop.stop()
#     robot.say_text("Hello how are you today").wait_for_completed()
#
# def voiceActions(robot:cozmo.robot.Robot):
#     robot.say_text("What is your name").wait_for_completed()
#
# #cozmo.run_program(voiceActions)
# cozmo.run_program(voiceAction)
#
#
#
# # def voiceCommsAction(robot:cozmo.robot.Robot):
# #     robot.loop.stop()
# #     if robot.clearSpeech and ("Cozmo".lower() in arspeech.lower() or "Cosmo".lower() in agent5.speech.lower()):
# #         if "Move".lower() in agent5.speech.lower():
# #             face= agent1.findCurrentState(robot)
# #             distance = face.pose.x
# #             robot.drive_straight(distance_mm(distance - float(250)),speed_mmps(50))
# #         else:
# #             robot.say_text("Testing this is a test").wait_for_completed()

import time
import asyncio
from threading import Thread

loopy = asyncio.get_event_loop()

#Example 2
def startLoop(loop):
    print("loop started")
    asyncio.set_event_loop(loop)
    loop.run_forever()

newLoop = asyncio.new_event_loop()
t = Thread(target=startLoop,args=(newLoop,))
t.start()

def moreWork(x):
    print("More work")
    time.sleep(x)
    print("Finished more")
    newLoop.call_soon_threadsafe(moreWork(6))

newLoop.call_soon_threadsafe(moreWork(3))

#Example 1
# async def doSomeWork(x):
#     print("Wait " + str(x))
#     await asyncio.sleep(x)
#
# tasks = [asyncio.ensure_future(doSomeWork(2)),asyncio.ensure_future(doSomeWork(5))]
# loop.run_until_complete(asyncio.gather(*tasks))
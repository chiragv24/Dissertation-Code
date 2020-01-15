# from QLearnSuperClass import QLearnDistOrthogonal
# from QLearnSuperClass import QLearnTurnOrthogonal
# from QLearnSuperClass import QLearnLiftOrthogonal
# from QLearnSuperClass import QLearnGreetOrthogonal
from asyncioTesting import QLearnDistOrthogonal
from asyncioTesting import QLearnGreetOrthogonal
from microIntegration import voiceIntegration
import cozmo
import threading
agent1 = QLearnDistOrthogonal()
agent2 = QLearnGreetOrthogonal()
agent5 = voiceIntegration()
import logging
from cozmo.util import distance_mm, speed_mmps
import asyncio
from threading import Thread
#
# loop = asyncio.get_event_loop()
#
# def startLoop(loop):
#     asyncio.set_event_loop(loop)
#     loop.run_forever()
#
# newLoop = asyncio.new_event_loop()
# t = Thread(target = startLoop,args=(newLoop,),daemon=True)
# t.start()

def cozmoDist():
    # if "Move".lower() in agent5.speech.lower() or "Stop".lower() in agent5.speech.lower():
    #     robotLoop = robot.loop
    #     robotLoop.stop()
    #     cozmo.conn.CozmoConnection.shutdown(cozmo.conn.CozmoConnection)
    #     cozmo.run_program(agent5.voiceCommsAction)
    cozmo.run_program(agent1.trainCozmo)
    #agent2.trainCozmo(robot)
    # cozmo.run_program(agent1.trainCozmo)
    #cozmo.run_program(agent2.trainCozmo)

def cozmoGreet():
    cozmo.run_program(agent2.trainCozmo)



#     cozmoDist()
#     cozmo.conn.CozmoConnection.shutdown(cozmo.conn.CozmoConnection)

#newLoop.call_soon_threadsafe(agent5.voiceComms)
#cozmoDist()
cozmoGreet()


# if "Move".lower() in agent5.speech.lower() or "Stop".lower() in agent5.speech.lower():
#     cozmo.conn.CozmoConnection.shutdown(cozmo.conn.CozmoConnection)
#     cozmo.run_program(agent5.voiceCommsAction())
# else:
#     cozmoDist()







# def ag1():
#     cozmo.run_program(agent1.trainCozmo)
#
# def voiceRecog():
#     #TRYING TO DO IT WITH THE SAME CONNECTION COZMO
#     # agent5.voiceComms(loop)
#     agent5.voiceComms()
#
#
# distOrthog = threading.Thread(name="dist",target=ag1)
# listenerThread = threading.Thread(name="dist",target=voiceRecog,daemon=True)
#
# def voiceCommsAction(robot: cozmo.robot.Robot):
#     robot.loop.stop()
#     if agent5.clearSpeech and ("Cozmo".lower() in agent5.speech.lower() or "Cosmo".lower() in agent5.speech.lower()):
#         if "Move".lower() in agent5.speech.lower():
#             face= agent1.findCurrentState(robot)
#             distance = face.pose.x
#             robot.drive_straight(distance_mm(distance - float(250)),speed_mmps(50))
#         else:
#             robot.say_text("Testing this is a test").wait_for_completed()
#
# def noGood(robot:cozmo.robot.Robot):
#     robot.loop.stop()
#     robot.say_text("No understand").wait_for_completed()
#
# if __name__=='__main__':
#     distOrthog.start()
#     listenerThread.start()
#     if distOrthog.isAlive:
#         if agent5.clearSpeech:
#             cozmo.run_program(voiceCommsAction)
#             listenerThread.start()
#         else:
#             cozmo.run_program(noGood)




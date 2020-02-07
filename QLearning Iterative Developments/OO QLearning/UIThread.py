# from tkinter import *
import asyncio
from threading import Thread
# import threading
from uiTestingWorkerCode import mainWorker
import tkinter as tk

class UI():
    #Use text label in the other case if doesn't work
    def __init__(self):
        self.worker = mainWorker()
        self.root = tk.Tk()
        self.root.geometry('300x70')
        self.root.title("Commands and Score")
        self.bVoice = tk.StringVar()
        self.voice = tk.StringVar()
        self.q = tk.StringVar()
        self.blabel = tk.Label(self.root,textvariable = self.bVoice, width=100,bg="red")
        self.blabel.pack()
        self.vlabel = tk.Label(self.root,textvariable= self.voice,width=100,bg="blue")
        self.vlabel.pack()
        self.qlabel = tk.Label(self.root,textvariable = self.q,width=100,bg="red")
        self.qlabel.pack()

    def updateLabels(self):
        self.bVoice.set("Your background commands: " + self.worker.backVoice.speech)
        self.voice.set("Your score commands: " + self.worker.voice.speech)
        self.q.set("The Q-Matrix " + str(self.worker.agent1.Q))
        self.root.after(5000,self.updateLabels)

    def startWorker(self):
        self.worker.makeThread()
        self.worker.makeWorker()

    def runLoop(self):
        self.startWorker()
        self.root.after(5000,self.updateLabels)
        self.root.mainloop()


# worker = mainWorker()
# worker.makeThread()
# worker.makeWorker()
ui = UI()
# ui.bVoice.set("Your background commands: " + worker.backVoice.speech)
# ui.voice.set("Your score commands: " + worker.voice.speech)
# ui.q.set("The Q-Matrix " + str(worker.agent1.Q))
ui.runLoop()



# root = Tk()
#
# def ask_for_userInput():
#     userInput = input("Say your shit boi")
#     if userInput == "quit":
#         root.quit()
#     else:
#         label = Label(root,text = userInput)
#         label.pack(root,text=userInput)
#         root.after(2,ask_for_userInput())
#
#
# label = Label(root,text="What you said")
# root.after(2,ask_for_userInput())
# root.mainloop()

# def startLoop(loop):
#     asyncio.set_event_loop(loop)
#     loop.run_forever()
#
# def makeThread():
#     newLoopWorker = asyncio.new_event_loop()
#     t1 = Thread(target=startLoop, args=(newLoopWorker,))
#     t1.name = "KOBEEEEEEEEE"
#     t1.start()
#     newLoopWorker.call_soon_threadsafe(ask_for_userinput)
#     #asyncio.run_coroutine_threadsafe(cozmo.run_program(mainCode.cozmoDistHelper),newLoopWorker)
#     return t1
# #
# i = makeThread()
# master = Tk()
# w = Canvas(master,width=40,height=60)
# w.pack()
# canvas_height = 20
# canvas_width = 200
# y = int(canvas_height / 2)
# lab = Label(master, text)
# master.mainloop()
#
#
#
#

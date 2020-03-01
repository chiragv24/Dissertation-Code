from uiTestingWorkerCode import mainWorker
import tkinter as tk

class UI():
    #Use text label in the other case if doesn't work
    def __init__(self):
        self.worker = mainWorker()
        self.root = tk.Tk()
        self.root.geometry('')
        self.root.title("Commands and Score")
        self.bVoice = tk.StringVar()
        self.voice = tk.StringVar()
        self.q = tk.StringVar()
        self.blabel = tk.Label(self.root,textvariable = self.bVoice, width=2000,bg="red")
        self.blabel.config(font=("Calibri","30"))
        self.blabel.pack()
        self.vlabel = tk.Label(self.root,textvariable= self.voice,width=2000,bg="blue")
        self.vlabel.config(font=("Calibri","30"))
        self.vlabel.pack()
        self.qlabel = tk.Label(self.root,textvariable = self.q,width=2000,bg="red")
        self.qlabel.config(font=("Calibri","30"))
        self.qlabel.pack()

    def updateLabels(self):
        self.bVoice.set("Your background commands: " + self.worker.backVoice.speech)
        self.voice.set("Your score commands: " + self.worker.voice.speech)
        roundMatrix = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0]]
        for i in range (len(self.worker.agent1.Q)):
            for j in range (len(self.worker.agent1.Q[i])):
                roundMatrix[i][j] = round(self.worker.agent1.Q[i][j],2)
        self.q.set("The Q-Matrix " + str(roundMatrix))
        self.root.after(500,self.updateLabels)

    def startWorker(self):
        self.worker.makeThread()
        self.worker.makeWorker()

    def runLoop(self):
        self.startWorker()
        self.root.after(500,self.updateLabels())
        self.root.mainloop()

ui = UI()
ui.runLoop()


import matplotlib as mtp
from matplotlib import pyplot as plt
import decimal
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def rateGraph(rates):
    plt.figure()
    filenames = ["testdatafinalscorerate0.1.txt","testdatafinalscorerate0.25.txt","testdatafinalscorerate0.5.txt","testdatafinalscorerate0.75.txt","testdatafinalscorerate1.txt"]
    for j in range (len(filenames)):
        with open(filenames[j]) as f:
            lines = f.readlines()
            lines = lines[:-1]
            x = [line.split()[0] for line in lines]
            y = [line.split()[2] for line in lines]
            for i in range(len(y)):
                y[i] = float(y[i])
            plt.legend(["0.1", "0.25", "0.5", "0.75", "1.0"])
            plt.plot(x, y)
            plt.xlabel("Epochs")
            plt.ylabel("Average Score")
            plt.title("Comparison of scores with rate " + str(rates))

def ratevscoreGraph(filename,type):
    plt.figure()
    with open(filename) as f:
        lines = f.readlines()
        x = [line.split()[1] for line in lines]
        y = [line.split()[2] for line in lines]
        for i in range (len(x)):
            x[i] = float(x[i])
            y[i] = float(y[i])
    plt.plot(x,y)
    if type.lower() == "rate":
        plt.xlabel("Learning Rate")
        plt.ylabel("Average Score")
        plt.title("Comparison of Average Scores vs Learning Rate")
    else:
        plt.xlabel("Number of Epochs")
        plt.ylabel("Average Score")
        plt.title("Comparison of Average Scores vs Epochs")

def epochGraph(epochs):
    filenames = ["testdatafinalscoreepoch5.txt","testdatafinalscoreepoch25.txt","testdatafinalscoreepoch100.txt","testdatafinalscoreepoch200.txt","testdatafinalscoreepoch300.txt","testdatafinalscoreepoch400.txt"]
    for j in range (len(filenames)):
        with open(filenames[j]) as f:
            lines = f.readlines()
            lines = lines[:-1]
            x = [line.split()[1] for line in lines]
            y = [line.split()[2] for line in lines]
            for i in range(len(y)):
                y[i] = float(y[i])
            plt.plot(x, y)
            plt.legend(["5","25","100","200","300","400"])
            plt.xlabel("Learning Rate")
            plt.ylabel("Total Score")
            plt.title("Comparison of " + str(epochs) + " Epochs against Average Score")

def epochratescore(filename):
    fig = plt.figure()
    with open (filename) as f:
        lines = f.readlines()
        x =  [line.split()[0] for line in lines]
        y =  [line.split()[2] for line in lines]
        z =  [line.split()[1] for line in lines]
        for i in range(len(x)):
            x[i] = float(x[i])
            y[i] = float(y[i])
            z[i] = float(z[i])
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x,z,y)
        ax.set_title("Comparison of Epochs against Average Score and Rate")
        ax.set_xlabel('Epochs')
        ax.set_ylabel('Learning Rate')
        ax.set_zlabel('Total Score')
        #plt.show()

def gammaepochscore(filename,rate):
    fig = plt.figure()
    with open (filename) as f:
        lines = f.readlines()
        x =  [line.split()[3] for line in lines]
        y =  [line.split()[2] for line in lines]
        z =  [line.split()[0] for line in lines]
        for i in range(len(x)):
            x[i] = float(x[i])
            y[i] = float(y[i])
            z[i] = float(z[i])
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x,z,y)
        ax.set_title("Comparison of Discount Factor against Score and Epochs")
        ax.set_xlabel('Discount Factor')
        ax.set_ylabel('Epochs')
        ax.set_zlabel('Total Score')


def gammaratescore(filename, epochs):
    fig = plt.figure()
    with open(filename) as f:
        lines = f.readlines()
        x = [line.split()[3] for line in lines]
        y = [line.split()[2] for line in lines]
        z = [line.split()[1] for line in lines]
        for i in range(len(x)):
            x[i] = float(x[i])
            y[i] = float(y[i])
            z[i] = float(z[i])
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x, z, y)
        ax.set_title("Comparison of Discount Factor against Total Score and Rate with " + str(epochs) + " Epochs")
        ax.set_xlabel('Discount Factor')
        ax.set_ylabel('Learning Rate')
        ax.set_zlabel('Total Score')


def gammaGraph(epochs,rate):
    filenames = ["testscoregamma5epoch.txt","testscoregamma10epoch.txt","testscoregamma25epoch.txt","testscoregamma50epoch.txt","testscoregamma100epoch.txt","testscoregamma200epoch.txt","testscoregamma300epoch.txt","testscoregamma400epoch.txt"]
    plt.figure()
    for j in range(len(filenames)):
        with open(filenames[j]) as f:
            lines = f.readlines()
            x = [line.split()[3] for line in lines]
            y = [line.split()[2] for line in lines]
            for i in range(len(x)):
                x[i] = float(x[i])
                y[i] = float(y[i])
            plt.plot(x,y)
            plt.legend(["5", "10", "25", "50", "100", "200", "300", "400"])
            plt.xlabel("Discount Factor")
            plt.ylabel("Total Score")
            plt.title("Comparison of score with discount factors with " + str(epochs) +" and rate " + str(rate))


def gammaReward(filename,epochs,rate,gamma):
    plt.figure()
    with open(filename) as f:
        lines = f.readlines()
        x = [line.split()[3] for line in lines]
        y = [line.split()[2] for line in lines]
        for i in range(len(x)):
            x[i] = float(x[i])
            y[i] = float(y[i])
        plt.plot(x, y, 'bo')
        plt.xlabel("Training Iteration")
        plt.ylabel("Reward")
        plt.title("Comparison of rewards with Discount Factor " + str(gamma) + " with " + str(epochs) + " and rate " + str(rate))
        plt.show()

epochGraph([5,25,100,200,300,400])
rateGraph([0.1,0.25,0.5,0.75,1])
ratevscoreGraph("avgscorevrate.txt","rate")
ratevscoreGraph("avgscorevepoch.txt","epochs")
epochratescore("testfinalscorestotal.txt")
gammaepochscore("gammavepochsvscore.txt",0.25)
gammaratescore("epoch200vsgamma.txt",200)
gammaGraph([5,10,25,50,100,200,300,400],0.25)
gammaReward("trainData6rate0.25gamma0.1.txt",200,0.25,0.1)
gammaReward("trainData6rate0.25gamma0.25.txt",200,0.25,0.25)
gammaReward("trainData6rate0.25gamma0.5.txt",200,0.25,0.5)
gammaReward("trainData6rate0.25gamma0.75.txt",200,0.25,0.75)
gammaReward("trainData6rate0.25gamma1.txt",200,0.25,1)



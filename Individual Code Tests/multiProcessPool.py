import os
from multiprocessing import Pool

def method1():
    for i in range(10):
        print("Hello how are you doing today")

def method2():
    m = 0
    for i in range(100):
        m = m + 1
        print(m)


processes = ('method1','method2')

def runProcess(process):
    os.system('python {}'.format(process))

pool = Pool(processes=2)
pool.map(runProcess,processes)
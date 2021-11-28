import numpy as np
import pandas as pd

from Preprocessing import Preprocessing
from Problem import Problem
from LocalSearch import LocalSearch
from SM import SM
from ModSM import ModSM
import threading
import time

#A thread safe way to access shared variables between threads
semaphore = threading.Semaphore()

#Common variables
inputFilename = 'iku-fal17.xml'
groupname = 'iku-fal17_1K_Test' + str(int(time.time()))
iterations_budget = 1000

#Function to run Local Search
def runLS():
    #Acquire read access for file and other common variables
    semaphore.acquire()

    #Local Search Initialization with hyper parameters
    ls = LocalSearch(budget=iterations_budget, stopping_sp=500, problem= Problem(inputFilename), group=groupname)
    semaphore.release()
    #Read read access for file and other common variables so other threads can access it
    ls.solve()

def runSM():
    #Acquire read access for file and other common variables
    semaphore.acquire()
    #Simulated Annealing with with hyper parameters
    sm = SM(budget=iterations_budget, stopping_sp= 500, initial_temp= float(1e2),
        beta= float(6e-4), gamma = float(1e-4),
        problem= Problem(inputFilename), group=groupname)
    #Read read access for file and other common variables so other threads can access it
    semaphore.release()
    sm.solve()

def runMSM():
    #Acquire read access for file and other common variables
    semaphore.acquire()
    #Modified Simulated Annealing with with hyper parameters
    mod_sm = ModSM(budget=iterations_budget, stopping_sp=500, 
                initial_temp=1.0, age_limit=5,
                local_timeout_limit=5, rw_limit=40,
                steps=6, beta=float(6e-4), gamma = float(1e-4),
                problem= Problem(inputFilename), group=groupname)
    #Read read access for file and other common variables so other threads can access it
    semaphore.release()
    mod_sm.solve() 

#Starting LS Thread
LS_Thread = threading.Thread(target=runLS,name='LS_Thread')
LS_Thread.start()

#Starting SM Thread
SM_Thread = threading.Thread(target=runSM,name='SM_Thread')
SM_Thread.start()

#Starting MSM Thread
MSM_Thread = threading.Thread(target=runMSM,name='MSM_Thread')
MSM_Thread.start()

#Making the main thread wait until all threads are completed
LS_Thread.join()
SM_Thread.join()
MSM_Thread.join()

#Print group name
print(f'All algorithms ran on group')
print(groupname)
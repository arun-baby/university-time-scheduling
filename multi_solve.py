import numpy as np
import pandas as pd

from Preprocessing import Preprocessing
from Problem import Problem
from LocalSearch import LocalSearch
from SM import SM
from ModSM import ModSM
import threading
import time

semaphore = threading.Semaphore()

inputFilename = 'bet-sum18.xml'
groupname = 'bet-sum8_20000_' + str(int(time.time()))
iterations_budget = 20000

def runLS():
    semaphore.acquire()
    ls = LocalSearch(budget=iterations_budget, stopping_sp=500, problem= Problem(inputFilename), group=groupname)
    semaphore.release()
    ls.solve()

def runSM():
    semaphore.acquire()
    sm = SM(budget=iterations_budget, stopping_sp= 500, initial_temp= float(1),
        beta= float(6e-4), gamma = float(1e-4),
        problem= Problem(inputFilename), group=groupname)
    semaphore.release()
    sm.solve()

def runMSM():
    semaphore.acquire()
    mod_sm = ModSM(budget=iterations_budget, stopping_sp=500, 
                initial_temp=1.0, age_limit=5,
                local_timeout_limit=5, rw_limit=10,
                steps=5, beta=float(6e-4), gamma = float(1e-4),
                problem= Problem(inputFilename), group=groupname)
    semaphore.release()
    mod_sm.solve() 

LS_Thread = threading.Thread(target=runLS,name='LS_Thread')
LS_Thread.start()

SM_Thread = threading.Thread(target=runSM,name='SM_Thread')
SM_Thread.start()

MSM_Thread = threading.Thread(target=runMSM,name='MSM_Thread')
MSM_Thread.start()

LS_Thread.join()
SM_Thread.join()
MSM_Thread.join()

print(f'All algorithms ran on group')
print(groupname)
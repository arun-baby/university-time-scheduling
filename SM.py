import pandas as pd
from helpers import uploadDataFrame,uploadParams, mutate, coolTemperature, acceptanceProbability
from time import time, perf_counter
import threading
import math

import random

class SM:
    def __init__(self,budget, stopping_sp, 
                    initial_temp, age_limit, beta, gamma, problem ):

        self.EID = f'SM_{int(time())}'
        self.BUDGET = budget
        self.STOPPING_SP = stopping_sp
        self.INIT_TEMP = initial_temp
        self.AGE_LIMIT = age_limit
        self.BETA = beta
        self.GAMMA = gamma
        

        self.problem = problem

        self.thread = None

        self.lst_str_cols = ['EID', 'Iteration', 'Temperature', 'Best_SP', 'Current_SP', 'TimeElapsed']
        # use dictionary comprehension to make dict of dtypes
        dict_dtypes = {x : 'str'  for x in self.lst_str_cols}
        self.df = pd.DataFrame(columns=self.lst_str_cols)
        self.df.astype(str)


    def solve(self):

        self.EID = f'SM_{int(time())}'

        #Local timeout to 0
        local_timeout = 0
        #Setting best and current as initial solution
        self.problem.best = self.problem.initial_solution.copy()
        self.problem.current = self.problem.initial_solution.copy()
        #Setting local best to infinity
        local_best = math.inf
        #Setting stopping criteria to false
        met_criteria = False

        temp = self.INIT_TEMP

        i = 0

        row = [self.EID, i, temp, self.getBestSP(), self.getCurrentSP(), 0]

        self.df.loc[len(self.df)] = row

        while(not met_criteria):

            start, times = perf_counter(), {}

            temp = coolTemperature(temp, self.BETA)

            i = i+1

            candidate = mutate(self.problem.current)

            best_SP = self.getBestSP()
            candidate_SP = self.problem.getSearchPenalty(candidate)
            current_SP = self.getCurrentSP()

            print(f'candidate = current , {candidate==self.problem.current}')

            print(f'Iteration {i}: Temperature {temp}, Best SP: {best_SP}, Candidate SP {candidate_SP}, Current SP {current_SP}')

            if( candidate_SP < best_SP):
                self.problem.best = candidate.copy()
                print('Switching to new best')

            if(candidate_SP<current_SP):
                self.problem.current = candidate.copy()
                print('Switching to new current by primary condition')

            elif (acceptanceProbability(candidate, self.problem, temp,best_SP, self.GAMMA) > random.random()):
                print('Switching to new current by satisfying acceptance criteria')
                self.problem.current = candidate.copy()

            row = [self.EID, i, temp, self.getBestSP(), self.getCurrentSP(),  (-start + (start := perf_counter()))]
            self.df.loc[len(self.df)] = row

            if(i>(self.BUDGET-1)):
                met_criteria = True
                print('Stopping criteria met by going overbudget')

            if((best_SP<self.STOPPING_SP)):
                met_criteria = True
                print('Stopping criteria met by getting low penalty')

        params = {}
        params['EID'] = self.EID
        params['Filename'] = self.problem.filename
        params['BUDGET'] = self.BUDGET
        params['STOPPING_SP'] = self.STOPPING_SP
        params['type'] = 'Local Search'
        params['TotalIterations'] = i
        params['FinalSP'] = self.problem.getSearchPenalty(self.problem.best)

        uploadParams(params)
        uploadDataFrame(self.df,2)
        
            

    def getBestSP(self):
        return self.problem.getSearchPenalty(self.problem.best)
    
    def getCurrentSP(self):
        return self.problem.getSearchPenalty(self.problem.best)


    def solveAsync(self):
        self.thread = threading.Thread(target=self.solve,name=self.EID, daemon=True)
        self.thread.start()
        print('Solving using Local Search Asyncronously...')
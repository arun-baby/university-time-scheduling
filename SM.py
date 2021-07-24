import pandas as pd
from helpers import uploadDataFrame,uploadParams, mutate, coolTemperature, acceptanceProbability
from time import time, perf_counter
import threading
import math

import random

class SM:
    def __init__(self,budget, stopping_sp, 
                    initial_temp, beta, gamma, problem, group=None ):

        self.group = group

        self.EID = f'SM_{int(time())}'

        

        self.BUDGET = budget
        self.STOPPING_SP = stopping_sp
        self.INIT_TEMP = initial_temp
        self.BETA = beta
        self.GAMMA = gamma
        
        self.feasibility = False

        self.problem = problem

        self.thread = None

        self.lst_str_cols = ['EID', 'Iteration', 'Temperature', 'Best_SP', 'Current_SP', 'Feasibility', 'TimeElapsed']
        # use dictionary comprehension to make dict of dtypes
        dict_dtypes = {x : 'str'  for x in self.lst_str_cols}
        self.df = pd.DataFrame(columns=self.lst_str_cols)
        self.df.astype(str)


    def solve(self):

        self.EID = f'SM_{int(time())}'

        print(f'Starting of experiment {self.EID } of group {self.group}')


        #Setting best and current as initial solution
        self.problem.best = self.problem.initial_solution.copy()
        self.problem.current = self.problem.initial_solution.copy()
        
        #Setting stopping criteria to false
        met_criteria = False

        temp = self.INIT_TEMP

        i = 0

        best_SP, feasibility = self.getBestSP()

        row = [self.EID, i, temp, best_SP, self.getCurrentSP(),feasibility, 0]

        self.df.loc[len(self.df)] = row

        while(not met_criteria):

            start, times = perf_counter(), {}

            temp = coolTemperature(temp, self.BETA)

            i = i+1

            candidate = mutate(self.problem.current)

            best_SP,_ = self.getBestSP()
            candidate_SP,_ = self.problem.getSearchPenalty(candidate, False)
            current_SP = self.getCurrentSP()

            print(f'candidate = current , {candidate==self.problem.current}')

            print(f'Iteration {i}: Temperature {temp}, Best SP: {best_SP}, Candidate SP {candidate_SP}, Current SP {current_SP}')

            if( candidate_SP < best_SP):
                self.problem.best = candidate.copy()
                print('Switching to new best')

            randomThresh = random.random()

            print(f'Random Threshold: {randomThresh}') 

            if(candidate_SP<current_SP):
                self.problem.current = candidate.copy()
                print('Switching to new current by primary condition')

            elif (acceptanceProbability(candidate_SP, current_SP, temp, best_SP, self.GAMMA) > randomThresh):
                print('Switching to new current by satisfying acceptance criteria')
                self.problem.current = candidate.copy()

            elapsedTime = (-start + (start := perf_counter()))

            print(f'This iteration took {elapsedTime} seconds')

            new_bestSP, feasibility = self.getBestSP()

            row = [self.EID, i, temp, new_bestSP, self.getCurrentSP(),feasibility, elapsedTime]
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
        params['type'] = 'Simulated Annealing'
        params['TotalIterations'] = i
        finalSP, feasibility = self.getBestSP()
        params['FinalSP'] = finalSP
        params['Feasible'] = feasibility

        print(f'Final solution feasibility {feasibility}')

        self.feasibility = feasibility

        uploadParams(params, self.group)
        uploadDataFrame(self.df,2)
        
            

    def getBestSP(self):
        SP, feasibility = self.problem.getSearchPenalty(self.problem.best)
        return SP, feasibility
    
    def getCurrentSP(self):
        SP, feasibility = self.problem.getSearchPenalty(self.problem.current)
        self.feasibility = feasibility
        return SP


    def solveAsync(self):
        self.thread = threading.Thread(target=self.solve,name=self.EID, daemon=True)
        self.thread.start()
        print('Solving using Local Search Asyncronously...')
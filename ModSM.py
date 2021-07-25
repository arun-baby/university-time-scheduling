import pandas as pd
from helpers import uploadDataFrame,uploadParams, mutate, coolTemperature, acceptanceProbability
from time import time, perf_counter
import threading
import math

import random

class ModSM:
    def __init__(self,budget, stopping_sp, 
                    initial_temp, age_limit, local_timeout_limit, rw_limit, steps, beta, gamma, problem, group=None ):

        self.group = group

        self.EID = f'MSM_{int(time())}'
        self.BUDGET = budget
        self.STOPPING_SP = stopping_sp
        self.INIT_TEMP = initial_temp
        self.AGE_LIMIT = age_limit
        self.BETA = beta
        self.GAMMA = gamma
        self.RW_LIMIT = rw_limit
        self.LOCAL_TO_LIMIT = local_timeout_limit

        self.RW_SEPS = steps
        

        self.problem = problem

        self.thread = None

        self.lst_str_cols = ['EID', 'Iteration', 'Temperature', 'Best_SP', 'Current_SP',  'Feasibility', 'TimeElapsed']
        # use dictionary comprehension to make dict of dtypes
        dict_dtypes = {x : 'str'  for x in self.lst_str_cols}
        self.df = pd.DataFrame(columns=self.lst_str_cols)
        self.df.astype(str)


    def solve(self):

        self.EID = f'MSM_{int(time())}'

        print(f'Starting of experiment {self.EID } of group {self.group}')

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

            if(candidate_SP < local_best):
                local_best = candidate_SP
                local_timeout = 0
            else:
                local_timeout = local_timeout + 1

            print(f'Iteration {i}: Temperature {temp}, Best SP: {best_SP}, Candidate SP {candidate_SP}, Current SP {current_SP}, Local timeout {local_timeout}')

            if( candidate_SP < best_SP):
                self.problem.best = candidate.copy()
                print('Switching to new best')

            randomThresh = random.random()

            print(f'Random Threshold: {randomThresh}') 

            if(candidate_SP<current_SP):
                self.problem.current = candidate.copy()
                print('Switching to new current by primary condition')

            elif ((acceptanceProbability(candidate_SP, current_SP, temp, best_SP, self.GAMMA) - 0.1) > randomThresh):
                print('Switching to new current by satisfying acceptance criteria')
                self.problem.current = candidate.copy()

            #Reset if timeout limit is over
            if(local_timeout > self.LOCAL_TO_LIMIT ):
                #Reset SM parameters
                temp = self.INIT_TEMP
                local_best = math.inf
                local_timeout = 0
                #Increment timeouts of unsatisfied constraints
                self.problem.ageConstraints(True)

                #Get age of the oldest persistent hard constraint
                maxAge = self.problem.getMaxAge()
                
                #If solution is infeasible and the oldest age is more than age_limit, perform random walk
                if((not self.feasibility) and (maxAge > self.AGE_LIMIT)):
                    focusedConstraints = self.problem.getOldestHardConstraints()
                    self.problem.current = self.problem.performRandomWalk(self.problem.current.copy(), focusedConstraints, self.RW_LIMIT, self.RW_SEPS)
                    

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
        params['type'] = 'Modified Simulated Annealing'
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
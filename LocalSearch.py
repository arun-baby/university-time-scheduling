import pandas as pd
from helpers import uploadDataFrame,uploadParams, mutate
from time import time, perf_counter
import threading

class LocalSearch:
    def __init__(self,budget, stopping_sp, problem):
        
        self.EID = f'LS_{int(time())}'
        self.BUDGET = budget
        self.STOPPING_SP = stopping_sp
                # Generating pandas df for local search
        self.lst_str_cols = ['EID', 'Iteration', 'Best_SP', 'TimeElapsed']
        # use dictionary comprehension to make dict of dtypes
        dict_dtypes = {x : 'str'  for x in self.lst_str_cols}

        self.df = pd.DataFrame(columns=self.lst_str_cols)
        self.df.astype(str)
        self.problem = problem

        self.thread = None

    def solve(self):
        #Regenerating EID
        self.EID = f'LS_{int(time())}'
        
        self.df = pd.DataFrame(columns=self.lst_str_cols)
        self.df.astype(str)

        #setting best to initial solution
        self.problem.best = self.problem.initial_solution.copy()
        i = 0

        row = [self.EID, i,  self.problem.getSearchPenalty(self.problem.best),0]
        self.df.loc[len(self.df)] = row

        met_criteria = False

        params = {}
        
        while(not met_criteria):

            start, times = perf_counter(), {}

            i = i+1

            candidate = mutate(self.problem.best)

            best_SP = self.problem.getSearchPenalty(self.problem.best)

            candidate_SP = self.problem.getSearchPenalty(candidate)

            print(f'Iteration {i}: Best SP: {best_SP}, Candidate SP {candidate_SP}')

            if(candidate_SP<best_SP):
                self.problem.best = candidate.copy()
                print('Setting new best')


            row = [self.EID, i,  best_SP, (-start + (start := perf_counter()))]
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
        uploadDataFrame(self.df,1)


    def solveAsync(self):
        self.thread = threading.Thread(target=self.solve,name=self.EID, daemon=True)
        self.thread.start()
        
        print('Solving using Local Search Asyncronously...')
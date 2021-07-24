from Preprocessing import Preprocessing

from itertools import combinations
import random
from helpers import isOverlapped, getSameDays, getSameTimeslots, returnAge

class Problem:

    def __init__(self, inputFilename) -> None:

        hards = ['NotOverlap', 'SameAttendees']
        softs = ['DifferentTime', 'DifferentDays']

        self.filename = inputFilename
        
        self.courses = {}
        self.subparts ={}
        self.classes = {}
        self.hardConstraints = []
        self.softConstraints =[]
        self.students = []

        self.initial_solution = {}

        self.current = {}
        self.best = {}


        trimmedFile = Preprocessing.getTrimmedFile(inputFilename,
                         hards, softs)

        self.courses, self.subparts, self.classes, self.hardConstraints, self.softConstraints, self.students = Preprocessing.extractData(trimmedFile)
        
        for classID in self.classes.keys():
            self.initial_solution[classID] = (random.randrange(len(self.classes[classID].availTimes)), len(self.classes[classID].availTimes))

            
        print('Random solution initiated.')


    def getRandomSolution(self):
        random_solution = {}
        for classID in self.classes.keys():
            random_solution[classID] = (random.randrange(len(self.classes[classID].availTimes)), len(self.classes[classID].availTimes))
        return random_solution
    #print(solution_template[classID])

    def getHardPenalty(self, solution):
        #Total violations for all constraints
        totalHardViolations = 0

        #Iterating all hard constraints
        for hard in self.hardConstraints:
            #Check if type is 'NotOverlap'
            if hard.type == 'NotOverlap':

                #Getting list of classes for the corresponding constraint
                classList = hard.classes
                
                #Getting all possible pairs from the list
                pairs = list(combinations(classList, 2)) 
                
                singleConstraintViolation = 0
                #Iterating through all the pairs
                for pair in pairs:
                    #Unpacking thepair
                    class1ID, class2ID = pair
                    #Extracting class timings
                    class1Index,_ = solution[class1ID]
                    class2Index,_ = solution[class2ID]
                    class1Timing = self.classes[class1ID].availTimes[class1Index]
                    
                    class2Timing = self.classes[class2ID].availTimes[class2Index]

                    #Getting 'NonOverlap' violations
                    violations, dailyOverlap, count = isOverlapped(class1Timing, class2Timing)
                    
                    #Adding to total violations
                    singleConstraintViolation = singleConstraintViolation + violations
            
                if(singleConstraintViolation>0):
                    hard.satisfied = False
                else:
                    hard.satisfied = True
            

                totalHardViolations = totalHardViolations + singleConstraintViolation
        #print(f"Total Hard penalty: {totalHardViolations}")
        return totalHardViolations 


    #Get soft penalty
    def getSoftPenalty(self,solution):
        #Total violations for all constraints
        totalSoftPenalty = 0

        #Iterating all hard constraints
        for soft in self.softConstraints:
            #Getting list of classes for the corresponding constraint
            classList = soft.classes
            penalty = soft.penalty
                
            #Getting all possible pairs from the list
            pairs = list(combinations(classList, 2)) 
                
            constraintTotal = 0
            #Iterating through all the pairs
            for pair in pairs:
                #Unpacking thepair
                class1ID, class2ID = pair
                #Extracting class timings
                class1Index,_ = solution[class1ID]
                class2Index,_ = solution[class2ID]
                class1Timing = self.classes[class1ID].availTimes[class1Index]
                class2Timing = self.classes[class2ID].availTimes[class2Index]

                #Check for 'DifferentTime'
                if(soft.type == 'DifferentTime'):
                    overlaps = getSameTimeslots(class1Timing, class2Timing)
                    constraintTotal = constraintTotal + (overlaps*penalty)
                
                #Check for 'DifferentDays'
                elif(soft.type == 'DifferentDays'):
                    count = getSameDays(class1Timing, class2Timing)
                    constraintTotal = constraintTotal + (count*penalty)

            if(constraintTotal>0):
                soft.satisfied = False
            else:
                soft.satisfied = True

            #Adding to total soft penalty after multiplying with penalty corresponding to that soft constraint
            totalSoftPenalty = constraintTotal*int(soft.penalty)

        #print(f"Soft Penalty: {totalSoftPenalty}")
        return totalSoftPenalty 


    #Get penalty of timings
    def getTimingPenalty(self,solution):
        #Timing penalty calculation
        totalTimingPenalty = 0

        #Iterating through all the classes
        for classID in self.classes.keys():
            #Getting selected timing from each class
            selectedIndex,_ = solution[classID]
            selectedTiming = self.classes[classID].availTimes[selectedIndex]
            #Adding penalty of selected timing to total timings penalty
            totalTimingPenalty = totalTimingPenalty + int(selectedTiming.penalty)

        #print(f"Timing Penalty: {totalTimingPenalty}")
        return totalTimingPenalty

    
    #Incrementing interations and timeout counts in constraints
    def ageConstraints(self,timeout):
        for hard in self.hardConstraints:
            if(hard.satisfied):
                hard.iterations = 0
                hard.timeouts = 0
            else:
                hard.iterations = hard.iterations + 1
                if(timeout):
                    hard.timeouts = hard.timeouts + 1
        for soft in self.softConstraints:
            if(soft.satisfied):
                soft.iterations = 0
                soft.timeouts = 0
            else:
                soft.iterations = soft.iterations + 1
                if(timeout):
                    soft.timeouts = soft.timeouts + 1



    #Get the age of the oldest constraint
    def getMaxAge(self):
        self.hardConstraints.sort(reverse=True,key=returnAge)
        return self.hardConstraints[0].timeouts


    #Check if the given solution is infeasible
    def isInfeasible(self, solution):
        return (Problem.getHardPenalty(self, solution) > 0)

    #Function to calculate search penalty
    def getSearchPenalty(self,solution):
        return 10*self.getHardPenalty(solution) + self.getSoftPenalty(solution) + self.getTimingPenalty(solution)




            

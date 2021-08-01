
#Check for two timings for DifferentTime constraints
def getSameTimeslots(timing1, timing2):
    #getting start and end times for both timings
    t1start = int(timing1.start)
    t2start = int(timing2.start)
    t1end = t1start + int(timing1.length)
    t2end = t2start + int(timing2.length)

    #Total overlap in time regardless of day or week
    overlapLength = 0

    #Calculates the daily overlap if classes occur at any same day
    if(t1end >= t2start):
        overlapLength = t1end - t2start + 1
    elif(t2end >= t1start):
        overlapLength = t2end - t1start + 1

    #print(f"Overlapping timeslots: {overlapLength}")
    #Returns the overlap length
    return overlapLength

#Check for timings for DifferentDay timings 
def getSameDays(timing1, timing2):
    #getting days data from both timings
    t1d = list(timing1.days)
    t2d = list(timing2.days)

    #Count for days overlapped
    count = 0
    #Iterate through all days of the the week
    for i in range(0, 7):
        #Checks if class occur on the same day at any day of the semester
        if (t1d[i] == t2d[i]) and (t1d[i]==1):
            #Add one to days overlapped
            count = count + 1

    #print(f"Overlapping days: {count}")
    #return number of days the classes occur on the same day
    return count

#function to check if 2 timings are overlapping
def isOverlapped(timing1, timing2):
    #getting start and end times for both timings
    t1start = int(timing1.start)
    t2start = int(timing2.start)
    t1end = t1start + int(timing1.length)
    t2end = t2start + int(timing2.length)
    #Count of overlapping days
    count = 0

    
    #number of 5-min timeslots overlapped
    dailyOverlap = 0

    #this if is to check if the time of the classes are overlapping. 
    #classes will overlap only if the time of the class overlap on any day
    if (t1end >= t2start) or (t2end >= t1start):
        #interate through all days of the semester
        for i in range(0, timing1.tdays_np.size):
            #Checks if class occur on the same day at any day of the semester
            if (timing1.tdays_np[i] + timing2.tdays_np[i]) == 2:
                #Add one to days overlapped
                count = count + 1
        #Calculates the daily overlap if classes occur at any same day
        if(count>0):
            if(t1end >= t2start):
                dailyOverlap = t1end - t2start + 1
            elif(t2end >= t1start):
                dailyOverlap = t2end - t1start + 1

    #Total 5-min timeslots overlapped in a semester
    violations = count*dailyOverlap
    #print(f"Total timeslot overlaps: {violations}, daily overlap: {dailyOverlap}, days overlapped: {count}")
    return violations, dailyOverlap, count

from itertools import combinations
#Get Hard penalty
def getHardPenalty(solution, hardConstraints, classes):
    #Total violations for all constraints
    totalHardViolations = 0

    #Iterating all hard constraints
    for hard in hardConstraints:
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
                class1Timing = classes[class1ID].availTimes[class1Index]
                
                class2Timing = classes[class2ID].availTimes[class2Index]

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
def getSoftPenalty(solution, softConstraints, classes):
    #Total violations for all constraints
    totalSoftPenalty = 0

    #Iterating all hard constraints
    for soft in softConstraints:
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
            class1Timing = classes[class1ID].availTimes[class1Index]
            class2Timing = classes[class2ID].availTimes[class2Index]

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
def getTimingPenalty(solution, classes):
    #Timing penalty calculation
    totalTimingPenalty = 0

    #Iterating through all the classes
    for classID in classes.keys():
        #Getting selected timing from each class
        selectedIndex,_ = solution[classID]
        selectedTiming = classes[classID].availTimes[selectedIndex]
        #Adding penalty of selected timing to total timings penalty
        totalTimingPenalty = totalTimingPenalty + int(selectedTiming.penalty)

    #print(f"Timing Penalty: {totalTimingPenalty}")
    return totalTimingPenalty

import random

# Function to mutate a given solution
def mutate(solution):
    mutation = solution.copy()
    #Creating a list of keys(classIDs)
    indexList = list(mutation.keys())
    #Getting a random classID from the list
    randomClass = indexList[random.randrange(len(indexList))]
    #print(solution)
    #Extracting the timing info of that class
    timingIndex,timingsLen = mutation[randomClass]

    #Reducing the probabilty of not having a mutation. If a class is selected with a single timing, mutation is not possible. 
    if timingsLen == 1:
        for i in range(10):
            randomClass = indexList[random.randrange(len(indexList))]
            timingIndex,timingsLen = mutation[randomClass]
            if(timingsLen>1):
                break
    #Mutating the index
    if(timingsLen != 1):
        newIndex = (timingIndex+random.randrange(timingsLen-1)+1)%timingsLen
        mutation[randomClass] = (newIndex, timingsLen)
        #print(f"Mutating class {randomClass} from timing index {timingIndex} to {newIndex} out of {timingsLen} timings")
    else:
        print('No mutation')

    #Replacing the dictionary value
    
    #print(solution)
    return mutation

#Incrementing interations and timeout counts in constraints
def ageConstraints(timeout, hardConstraints, softConstraints):
    for hard in hardConstraints:
        if(hard.satisfied):
            hard.iterations = 0
            hard.timeouts = 0
        else:
            hard.iterations = hard.iterations + 1
            if(timeout):
                hard.timeouts = hard.timeouts + 1
    for soft in softConstraints:
        if(soft.satisfied):
            soft.iterations = 0
            soft.timeouts = 0
        else:
            soft.iterations = soft.iterations + 1
            if(timeout):
                soft.timeouts = soft.timeouts + 1


#Cooling function
def coolTemperature(temperature, beta):
    return temperature / (1.0 + beta * temperature)

#Return the age of the constraint
def returnAge(hard):
    return hard.timeouts


#Sort the Hardconstraint in descending order of timeouts
def sortHardConstraints(hardConstraints):
   hardConstraints.sort(reverse=True,key=returnAge)


#Get the age of the oldest constraint
def getMaxAge(hardConstraints):
    sortHardConstraints()
    return hardConstraints[0].timeouts


#Check if the given solution is infeasible
def isInfeasible(solution):
    return (getHardPenalty(solution) > 0)

#Getting the oldest constraints that persisted max timeouts
def getOldestHardConstraints(hardConstraints):
    sortHardConstraints()
    return hardConstraints[:10]


import math

#Function to calculate search penalty
def getSearchPenalty(solution):
    return getHardPenalty(solution) + getSoftPenalty(solution) + getTimingPenalty(solution)


#Energy function
def calculateEnergy(searchPenalty, bestPenalty, gamma):

    energyPower = -1*gamma*(searchPenalty - bestPenalty)
    energy = 1 - math.exp(energyPower)
    #print(f'Solution Penalty {searchPenalty}, Best Penalty {bestPenalty}, Energy Power {energyPower}, Energy: {energy}')
    return energy
    
#calculate the acceptance probability of the candidate
def acceptanceProbability(candidate_SP, current_SP, temperature, SPB, gamma):
    currentEnergy = calculateEnergy(current_SP, SPB,gamma)
    candidateEnergy = calculateEnergy(candidate_SP, SPB, gamma)
    if(candidateEnergy < currentEnergy):
        probability = 1
    else:
        probPower = (currentEnergy-candidateEnergy)/temperature
        probability = math.exp(probPower)
       # print(f'Probability power: {probPower}')

    print(f'Probability: {probability}')

    return probability


#Function to get penalty only on a few focused hard constraints
def getFocusedPenalty(solution, focusedConstraints, classes):
    #Total violations for all focused constraints
    totalHardViolations = 0

    #Iterating all hard constraints
    for hard in focusedConstraints:
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
                class1Timing = classes[class1ID].availTimes[class1Index]
                
                class2Timing = classes[class2ID].availTimes[class2Index]

                #Getting 'NonOverlap' violations
                violations, dailyOverlap, count = isOverlapped(class1Timing, class2Timing)
                
                #Adding to total violations
                singleConstraintViolation = singleConstraintViolation + violations
           
            if(singleConstraintViolation>0):
                hard.satisfied = False
            else:
                hard.satisfied = True
           

            totalHardViolations = totalHardViolations + singleConstraintViolation
    print(f"Focused penalty: {totalHardViolations}")
    return totalHardViolations

import numpy as np

#Perform random walk for a distance

def randomWalk(solution, distance, classSet):
    
    #Possible steps for any class
    step_set = [-1, 0, 1]

    #perform randomwalk for given distance
    for i in range(distance):
        for eachClass in classSet:
            #Generates a random step with equal probability for each class 
            step = np.random.choice(step_set)
            timingIndex,timingsLen = solution[eachClass]
            #Can have a negative value of just -1. We will then given the index of the last timing.
            if (timingIndex+step) < 0:
                newIndex = timingsLen - 1
            else:
                newIndex = (timingIndex+step)%timingsLen
            
            solution[eachClass] = (newIndex, timingsLen)

    return solution
            

#The function to perform random walk on a focused constraints
def performRandomWalk(solution, focusedConstraints, classes):
    classSet = set()

    #Adding all classes in all the constriants to a set
    for focus in focusedConstraints:
        classList = focus.classes
        for one in classList:
            #Adding to a set since duplicates will be ignored
            classSet.add(one)

    timeout = 0
    timeout_limit = 10

    #Return the solution if a better candidate is not acheived even after timeout_limit iterations
    while(timeout < timeout_limit):
        #Performing random walk for a distance of 5 steps
        candidate = randomWalk(solution.copy(), 5, classes)
        #Check if candidate is better than solution using focused penalty
        if(getFocusedPenalty(candidate, focusedConstraints) < getFocusedPenalty(solution, focusedConstraints)):
            solution = candidate
            timeout = 0
        else:
            timeout = timeout + 1

    return solution


from google.cloud import firestore
def uploadParams(params, group):
    db = firestore.Client.from_service_account_json('utp-320721-e1afef9ba011.json')

    if group is None:
        print('Individual experiment')
        doc_ref = db.collection('experiments').document(params['EID'])
        doc_ref.set(params)

    else:
        print(f'Experiment Group: {group}')
        group_Ref = db.collection('experimentGroups').document(group)
        doc_ref = group_Ref.collection('experiments').document(params['EID'])
        doc_ref.set(params)

    
    print('Uploaded parameters to Firestore')

from google.oauth2 import service_account
import pandas_gbq

def uploadDataFrame(df, type):
    credentials = service_account.Credentials.from_service_account_file(
    'utp-320721-e1afef9ba011.json',
    )
    if(type==1):
        schema = []
        schema.append({'name': 'EID','type': 'STRING'})
        schema.append({'name': 'Iteration','type': 'INTEGER'})
        schema.append({'name': 'Best_SP','type': 'INTEGER'})
        schema.append({'name': 'Feasibility','type': 'BOOLEAN'})
        schema.append({'name': 'TimeElapsed','type': 'FLOAT'})

        pandas_gbq.to_gbq(
    df, 'utp-320721.experiments.experimentLog', project_id='utp-320721', if_exists='append', credentials=credentials, table_schema=schema
)

    elif(type==2):
        schema = []
        schema.append({'name': 'EID','type': 'STRING'})
        schema.append({'name': 'Iteration','type': 'INTEGER'})
        schema.append({'name': 'Best_SP','type': 'INTEGER'})
        schema.append({'name': 'Temperature','type': 'FLOAT'})
        schema.append({'name': 'Current_SP','type': 'INTEGER'})
        schema.append({'name': 'Feasibility','type': 'BOOLEAN'})
        schema.append({'name': 'RandomWalk','type': 'BOOLEAN'})
        schema.append({'name': 'TimeElapsed','type': 'FLOAT'})

        pandas_gbq.to_gbq(
    df, 'utp-320721.experiments.experimentLog', project_id='utp-320721', if_exists='append', credentials=credentials, table_schema=schema
)
    print('Uploaded datafram to BigQuery')

from google.cloud import bigquery

bqclient = bigquery.Client.from_service_account_json('utp-320721-e1afef9ba011.json')
def getSingleExp_df(EID, columns):

    print(f'Getting data from experiment {EID}, with columns {columns}')

    query_string = f"""
    SELECT {columns}
    FROM `utp-320721.experiments.experimentLog` 

    WHERE EID = '{EID}'

    ORDER BY Iteration
    """

    dataframe = (
        bqclient.query(query_string)
        .result()
        .to_dataframe(
            create_bqstorage_client=True,
        )
    )

    return dataframe


def getRandomWalks(EID):
    columns = 'Iteration, Best_SP, RandomWalk'
    query_string = f"""
        SELECT {columns}
        FROM `utp-320721.experiments.experimentLog` 

        WHERE EID = '{EID}' and RandomWalk = true

        ORDER BY Iteration
        """

    return (
            bqclient.query(query_string)
            .result()
            .to_dataframe(
                create_bqstorage_client=True,
            )
        )

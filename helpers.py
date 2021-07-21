
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

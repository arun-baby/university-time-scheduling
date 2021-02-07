import xml.etree.ElementTree as ET 
import os

import xml.etree.ElementTree as ET

#Extracting the custom classes from the Components module, See components folder for class definitions
from Components.Class import Class
from Components.Course import Course
from Components.HardConstraint import HardConstraint
from Components.SoftConstraint import SoftConstraint
from Components.Student import Student
from Components.Subpart import Subpart
from Components.Timing import Timing




class Preprocessing:
    def getTrimmedFile(path, hards, softs):
        inputFilename = path
        # Passing the path of the 
        # xml document to enable the 
        # parsing process 
        tree = ET.parse(inputFilename) 

        #getting just the filename without extension for output file name
        trimmedName = os.path.splitext(inputFilename)[0]

        # getting the parent tag of 
        # the xml document 
        root = tree.getroot() 

        #Find and remove rooms tag
        rooms = root.find('rooms')
        root.remove(rooms)

        #Find optimization tag
        optimization = root.find('optimization')
        root.remove(optimization)

        #Find courses tags
        courses = root.find('courses')

        #Getting all classes from all courses
        classes = courses.findall('./course/config/subpart/class')

        #Removig all room children from each class parent
        for Class in classes:
            if(Class.get('room') != None):
                Class.attrib.pop('room')
            rooms = Class.findall('./room')
            for room in rooms:
                Class.remove(room)

        distRoot = root.find('distributions')

        #Finding and removing same-room constraints
        distributionsXML = distRoot.findall('./distribution')
        #Listing the required types of constraints to be extracted
        #softTypes = ['SameTime', 'DifferentTime', 'MinGap', 'DifferentDays']
        softTypes = softs
        #hardTypes = ['Precedence', 'SameAttendees', 'NotOverlap']
        hardTypes = hards
        #Iterating through all distribution constraints

        for dist in distributionsXML:
            #getting type of constraints to be checked
            constraintType = dist.get('type')
            #Removing the () from MinGap(G) for simpler comparison
            constraintType = constraintType.split('(')[0]
            #Setting default value to False for keeping current constraint
            keep = False
            #Checking if the current type is in Soft constraint types
            if constraintType in softTypes:
                #Checking if the given constraint is soft (all soft constriants will have penalty value)
                if dist.get('penalty') is not None:
                    keep = True

            #Checking if the current type is in Hard constraint types
            elif constraintType in hardTypes:
                #Checking if the given constraint is hard (all hard constriants will have reqired as true)
                if(dist.get('required') == 'true'):
                    keep = True
                    #Replacing SameAttendees with NotOverlap
                    if constraintType in 'SameAttendees':
                        dist.set('type', 'NotOverlap')

            #If the current constraint is not required, the keep value is never changed to True and hence removing the same from constraints
            if keep is False:
                distRoot.remove(dist)

        outputFilename = trimmedName + '_trimmed.xml'
        tree.write(outputFilename)

        with open(inputFilename) as myfile:
            head = [next(myfile) for x in range(1)]

        with open(outputFilename, 'r') as trimmed:
            content = trimmed.read() 


        with open(outputFilename, 'w') as trimmed:
            trimmed.seek(0,0)
            trimmed.write(head[0]+'\n'+content)

        return outputFilename

    def extractData(path):
        inputFile = path
        # Passing the path of the 
        # xml document to enable the 
        # parsing process 
        tree = ET.parse(inputFile) 
        # getting the parent tag of 
        # the xml document 
        root = tree.getroot() 
        #extracting just courses
        coursesXML = root.findall('./courses/course')

        #Initializing empty dictionaries
        courses = {}
        subparts = {}
        classes = {}

        #Iterating through each course's XML
        for course in coursesXML:
            #Finding the first config, other configs are not considered
            config = course.find('config')
            courseID = course.get('id')

            #Extracting all subparts in courseXML
            subpartXML = config.findall('subpart')
            #listing subparts to be added to course object
            subpartList = []
            for subpart in subpartXML:
                subpartID = subpart.get('id')
                subpartList.append(subpartID)

                #Finding all classes from Subpart XML
                classesXML = subpart.findall('class')
                #Listing all classes to be added to subpart object
                classList = []
                for singleClass in classesXML:
                    classID = singleClass.get('id')
                    classList.append(classID)
                    classLimit = singleClass.get('limit')
                    classParent = singleClass.get('parent')

                    #Finding all timings from Class XML
                    timeXML = singleClass.findall('time')
                    #Listing all timings to be added to Class object
                    timings = []
                    for timing in timeXML:
                        days = timing.get('days')
                        length = timing.get('length')
                        penalty = timing.get('penalty')
                        start = timing.get('start')
                        weeks = timing.get('weeks')
                        timingObject = Timing(days, length, start, weeks, penalty)
                        timings.append(timingObject)
                    #Creating a new class object
                    classObject = Class(classID, classLimit, classParent, subpartID, courseID, timings)
                    #Adding the new class object to class dictionary
                    classes[classID] = classObject
                #Creating a new subpart object
                subpartObject = Subpart(subpartID, courseID, classList)
                #Adding the new subpart object to class dictionary
                subparts[subpartID] = subpartObject
            #Creating a new course object
            courseObject = Course(courseID, subpartList)
            #Adding the new subpart object to class dictionary
            courses[courseID] = courseObject
        print("%d Classes extracted"%(len(classes)))
        print("%d Subparts extracted"%(len(subparts)))
        print("%d Courses extracted"%(len(courses)))

        #Initializing constraint lists
        hardConstraints = []
        softConstraints = []

        #Finding all the distribution constraints from root
        distributionXML = root.findall('./distributions/distribution')

        #Listing the required types of constraints to be extracted
        #requiredTypes = ['Precedence', 'NotOverlap', 'SameTime', 'DifferentTime', 'MinGap', 'DifferentDays']
        requiredTypes = ['NotOverlap', 'DifferentTime', 'DifferentDays']

        #Iterating through all distribution constraints
        for dist in distributionXML:
            #getting type of constraints to be checked
            constraintType = dist.get('type')
            #Removing the () from MinGap(G) for simpler comparison
            constraintType = constraintType.split('(')[0]

            #Checking if the current distribution's type matches any of the required types
            if constraintType in requiredTypes:
                #finding all classIDs and then appending to a list
                classList = []
                classXML = dist.findall('class')
                for singleClass in classXML:
                    classList.append(singleClass.get('id'))
                #Check if constraint is hard, if yes, adding it to hard constraints
                if(dist.get('required') == 'true'):
                    hardConstraints.append(HardConstraint(constraintType, classList))
                #If not, adding it to soft constraints
                else:
                    penalty = dist.get('penalty')
                    softConstraints.append(SoftConstraint(constraintType, classList, penalty))

        print("%d Hard Constraints extracted"%(len(hardConstraints)))
        print("%d Soft Constraints extracted"%(len(softConstraints)))
        students = []
        #Finding all students in XML
        studentXML = root.findall('./students/student')

        #Iterating through all student XMLs
        for stud in studentXML:
            studentId = stud.get('id')
            #Finding and listing all courses enrolled
            courseXML = stud.findall('course')
            courseList = []
            for singleCourse in courseXML:
                courseID = singleCourse.get('id')
                courseList.append(courseID)
                #From the courses dictionary, getting the corresponding course class and appending the studentID to that course
                courses[courseID].addStudent(studentId)
            #Appending the new student object to student list
            students.append(Student(studentId, courseList))

        print("%d Students extracted"%(len(students)))

        return (courses, subparts, classes, hardConstraints, softConstraints, students)

if __name__ == '__main__':
    Preprocessing.extractData('./agh-fis-spr17_trimmed.xml')
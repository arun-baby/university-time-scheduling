class Course:
    def __init__(self, id, subparts):
        self.id = id
        self.subparts = subparts
        self.students = []

    def addStudent(self, student):
        self.students.append(student)
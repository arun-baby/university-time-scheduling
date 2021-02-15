class Class:
    def __init__(self, id, limit, parent, subpart, course, availTimes):
        self.id = id
        self.limit = limit
        self.parent = parent
        self.subpart = subpart
        self.course = course
        self.availTimes = availTimes
        self.classConstraints = []
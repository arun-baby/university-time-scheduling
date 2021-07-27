class HardConstraint:
    def __init__(self, type, classes):
        self.type = type
        self.classes = classes
        self.iterations = 0
        self.timeouts = 0
        self.satisfied = False
        self.scale = 1
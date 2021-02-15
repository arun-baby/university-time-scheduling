class SoftConstraint:
    def __init__(self, type, classes, penalty):
        self.type = type
        self.classes = classes
        self.penalty = int(penalty)
        self.iterations = 0
        self.timeouts = 0
        self.satisfied = False
        self.scale = 1
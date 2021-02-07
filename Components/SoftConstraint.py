class SoftConstraint:
    def __init__(self, type, classes, penalty):
        self.type = type
        self.classes = classes
        self.penalty = int(penalty)
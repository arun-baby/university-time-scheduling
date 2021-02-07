import numpy as np

class Timing:
    def __init__(self, days, length, start, week, penalty):
        self.days = days
        self.length = int(length)
        self.start = int(start)
        self.week = week
        self.penalty = int(penalty)
        
        weeks = list(week)
        days = list(days)
        totalDays = len(weeks) * len(days)
        self.tdays_np = np.empty(totalDays)
        for i in range(0,len(weeks)):
            for j in range(0, len(days)):
                if (weeks[i] == '1') and (days[j] == '1'):
                    self.tdays_np[(i*7)+j] = 1
                else:
                    self.tdays_np[(i*7)+j] = 0

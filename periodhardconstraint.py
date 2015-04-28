class PeriodHardConstraint(object):

    def __init__(self, constraint="", first=0, second=0):
        self.constraint = constraint
        self.first = first
        self.second = second

    def __repr__(self):
        return 'PeriodHardConstraint(Constraint: {}, first: {}, second: {})'.format(self.constraint, self.first, self.second)

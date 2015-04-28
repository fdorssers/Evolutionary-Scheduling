class RoomHardConstraint(object):

    def __init__(self, constraint="", first=0, second=0):
        self.constraint = constraint
        self.first = first

    def __repr__(self):
        return 'RoomHardConstraint(Constraint: {}, first: {})'.format(self.constraint, self.first)

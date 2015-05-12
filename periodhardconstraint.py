from enum import Enum


class PeriodHardConstraint(object):

    def __init__(self, constraint, first=0, second=0):
        self.constraint = constraint
        self.first = first
        self.second = second

    def __repr__(self):
        return 'PeriodHardConstraint(Constraint: {}, first: {}, second: {})'.format(self.constraint, self.first, self.second)


class PeriodHardEnum(Enum):
    EXAM_COINCIDENCE = 1
    EXCLUSION = 2
    AFTER = 3

    @classmethod
    def fromstring(cls, str):
        return getattr(cls, str.upper(), None)

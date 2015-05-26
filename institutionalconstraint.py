from enum import Enum


class InstitutionalConstraint(object):
    def __init__(self, constraint="", values=[]):
        self.constraint = constraint
        self.values = values

    def __repr__(self):
        return 'InstitutionalConstraint(Constraint: {},value_list: {})'.format(self.constraint, self.values)


class InstitutionalEnum(Enum):
    TWOINAROW = 1
    TWOINADAY = 2
    PERIODSPREAD = 3
    NONMIXEDDURATIONS = 4
    FRONTLOAD = 5

    @classmethod
    def fromstring(cls, str):
        return getattr(cls, str.upper(), None)

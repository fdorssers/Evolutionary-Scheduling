class InstitutionalConstraint(object):

    def __init__(self, constraint="", value_single=-1, value_list=[]):
        self.constraint = constraint
        self.value_single = value_single
        self.value_list = value_list

    def __repr__(self):
        return 'InstitutionalConstraint(Constraint: {}, value_single: {}, value_list: {})'.format(self.constraint, self.value_single, self.value_list)

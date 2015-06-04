import fitness
from exam import Exam
from institutionalconstraint import InstitutionalConstraint
from institutionalconstraint import InstitutionalEnum

institutional_constraint = {
    InstitutionalEnum.PERIODSPREAD: InstitutionalConstraint(InstitutionalEnum.PERIODSPREAD, [3])}

periods = [1, 2, 3, 4]  # Filler data, only length matters

schedule = [(0, 0), (1, 1), (2, 1), (3, 3)]

exams = [Exam(10, [0, 1, 2]), Exam(10, [3, 4, 5]), Exam(10, [6, 7, 8]), Exam(10, [0, 6, 20]),  # Exam(10, [0, 3, 4]),
# Exam(10, [0, 1, 2]),
# Exam(10, [0, 1, 2])]

if __name__ == "__main__":
    penalty = fitness.period_spread_constraint4(schedule, exams, periods, institutional_constraint)
print('Penalty: {}'.format(penalty))


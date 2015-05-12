from exam import Exam
from period import Period
from room import Room
from periodhardconstraint import PeriodHardConstraint, PeriodHardEnum
from roomhardconstraint import RoomHardConstraint, RoomHardEnum
from institutionalconstraint import InstitutionalConstraint, InstitutionalEnum

EXAMS_HEADER = '[Exams:'
PERIOD_HEADER = '[Periods:'
ROOM_HEADER = '[Rooms:'
PERIOD_CONSTRAINTS_HEADER = '[PeriodHardConstraints]'
ROOM_CONSTRAINTS_HEADER = '[RoomHardConstraints]'
INSTITUTIONAL_CONSTRAINTS_HEADER = '[InstitutionalWeightings]'

HEADERS = [EXAMS_HEADER, PERIOD_HEADER, ROOM_HEADER, PERIOD_CONSTRAINTS_HEADER, ROOM_CONSTRAINTS_HEADER,
           INSTITUTIONAL_CONSTRAINTS_HEADER]


def parse_data(lines, header_start, header_end, function):
    return {i: function([v.strip() for v in line.split(',')]) for i, line in
            enumerate(lines[header_start + 1:header_end])}


def parse_constraint(lines, header_start, header_end, function, enum_function, constraint_enum):
    constraints = {c: [] for c in constraint_enum}
    for line in lines[header_start + 1:header_end]:
        vals = [l.strip() for l in line.split(',')]
        en = enum_function(vals)
        constraints[en].append(function(vals))
    return constraints


def parse():
    with open('data/exam_comp_set1.exam') as f:
        indices = {}
        lines = []
        for i, line in enumerate(f):
            if line.startswith('['):
                indices[determine_header(line)] = i
            lines.append(line.strip())
        exams = parse_data(lines, indices[EXAMS_HEADER], indices[PERIOD_HEADER], lambda x: Exam(int(x[0]), [int(i) for i in x[1:]]))
        periods = parse_data(lines, indices[PERIOD_HEADER], indices[ROOM_HEADER], lambda x: Period(x[0], x[1], int(x[2]), int(x[3])))
        rooms = parse_data(lines, indices[ROOM_HEADER], indices[PERIOD_CONSTRAINTS_HEADER], lambda x: Room(int(x[0]), int(x[1])))
        period_constraints = parse_constraint(lines, indices[PERIOD_CONSTRAINTS_HEADER], indices[ROOM_CONSTRAINTS_HEADER], lambda x: PeriodHardConstraint(PeriodHardEnum.fromstring(x[1]), int(x[0]), int(x[2])), lambda x: PeriodHardEnum.fromstring(x[1]), PeriodHardEnum)
        room_constraints = parse_constraint(lines, indices[ROOM_CONSTRAINTS_HEADER], indices[INSTITUTIONAL_CONSTRAINTS_HEADER], lambda x: RoomHardConstraint(RoomHardEnum.fromstring(x[1]), int(x[0])), lambda x: RoomHardEnum.fromstring(x[1]), RoomHardEnum)
        institutional_constraints = parse_constraint(lines, indices[INSTITUTIONAL_CONSTRAINTS_HEADER], len(lines), lambda x: InstitutionalConstraint(InstitutionalEnum.fromstring(x[0]), list(map(int, x[1:]))), lambda x: InstitutionalEnum.fromstring(x[0]), InstitutionalEnum)
        return exams, periods, rooms, period_constraints, room_constraints, institutional_constraints


def determine_header(line):
    for header in HEADERS:
        if line.startswith(header):
            return header
    return None


if __name__ == "__main__":
    parse()

from exam import Exam
from period import Period
from periodhardconstraint import PeriodHardConstraint
from room import Room
from roomhardconstraint import RoomHardConstraint


def parse_int_from_header(header):
    return int(''.join(x for x in header if x.isdigit()))


def parse_exams(f):
    nr_exams = parse_int_from_header(f.readline())
    exams = {}
    for i in range(nr_exams):
        vals = list(map(int, f.readline().split((','))))
        exams[i] = Exam(vals[0], vals[1:])
    return exams


def parse_periods(f):
    nr_periods = parse_int_from_header(f.readline())
    periods = {}
    for i in range(nr_periods):
        vals = f.readline().split((','))
        periods[i] = Period(vals[0], vals[1], int(vals[2]), int(vals[3]))
    return periods


def parse_rooms(f):
    nr_rooms = parse_int_from_header(f.readline())
    rooms = {}
    for i in range(nr_rooms):
        vals = list(map(int, f.readline().split((','))))
        rooms[i] = Room(vals[0], vals[1])
    return rooms


def parse_period_hard_constraints(f):
    # If it encounters this header it should stop
    room_header = '[RoomHardConstraints]'
    period_hard_constraints = []
    line = f.readline()
    while(room_header not in line):
        vals = line.split(',')
        period_hard_constraints.append(PeriodHardConstraint(vals[1], int(vals[0]), int(vals[2])))
        line = f.readline()
    return period_hard_constraints


def parse_room_hard_constraints(f):
    # If it encounters this header it should stop
    room_header = '[InstitutionalWeightings]'
    room_hard_constraints = []
    line = f.readline()
    while(room_header not in line):
        vals = line.split(',')
        room_hard_constraints.append(RoomHardConstraint(vals[1], int(vals[0])))
        line = f.readline()
    return room_hard_constraints


def parse_constraints(f):
    # Throw away period hard constraint
    f.readline()
    period_hard_constraints = parse_period_hard_constraints(f)
    room_hard_constraints = parse_room_hard_constraints(f)
    return period_hard_constraints, room_hard_constraints


def main():
    periods = {}
    with open('data/exam_comp_set1.exam') as f:
        exams = parse_exams(f)
        periods = parse_periods(f)
        rooms = parse_rooms(f)
        period_constraints, room_constraints = parse_constraints(f)


if __name__ == "__main__":
    main()

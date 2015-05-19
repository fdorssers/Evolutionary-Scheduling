import functools
from threading import Thread
from time import sleep
from periodhardconstraint import PeriodHardEnum
from roomhardconstraint import RoomHardEnum

MUCH = 1000


def naive_fitness(schedule, exams, periods, rooms, period_constraints, room_constraints, institutional_constraints):
    """
    Calculate the fitness of the schedule
    """
    conflict_fitness = conflict_constraint(schedule, period_constraints)
    room_occupancy_fitness = room_occupancy_constraint(schedule, exams, rooms)
    period_utilisation_fitness = period_utilisation_constraint(schedule, exams, periods)
    period_related_fitness = period_related_constraint(schedule, period_constraints)
    room_related_fitness = room_related_constraint(schedule, room_constraints)
    two_exams_in_a_row_fitness = two_exams_in_a_row_constraint(schedule, periods, exams)
    two_exams_in_a_day_fitness = two_exams_in_a_day_constraint(schedule, periods, exams)
    period_spread_fitness = period_spread_constraint(schedule, institutional_constraints)
    mixed_duration_fitness = mixed_duration_constraint(schedule)
    larger_exams_fitness = larger_exams_constraint(schedule, institutional_constraints)
    room_penalty_fitness = room_penalty_constraint(schedule, institutional_constraints)
    period_penalty_fitness = period_penalty_constraint(schedule, institutional_constraints)
    return (conflict_fitness, room_occupancy_fitness, period_utilisation_fitness, period_related_fitness,
            period_utilisation_fitness, room_related_fitness, two_exams_in_a_row_fitness, two_exams_in_a_day_fitness,
            period_spread_fitness, mixed_duration_fitness, larger_exams_fitness, room_penalty_fitness,
            period_penalty_fitness)

# Hard constraints


def conflict_constraint(schedule, period_constraints):
    """Returns penalty

    Two conflicting exams in the same period.
    """
    exam_coincidence_constraints = period_constraints[PeriodHardEnum.EXAM_COINCIDENCE]
    violations = 0
    for exam_coincidence_constraint in exam_coincidence_constraints:
        first_exam = schedule[exam_coincidence_constraint.first]
        second_exam = schedule[exam_coincidence_constraint.second]
        violations += first_exam[1] == second_exam[1]
    return violations


def room_occupancy_constraint(schedule, exams, rooms):
    """Returns penalty

    More seating required in any schedule period than that available.
    """
    violations = 0
    # Get mapping from room&period to ammount of students
    room_to_period_to_students = dict()
    for exam_i, (room, period) in enumerate(schedule):
        if room in room_to_period_to_students:
            if period in room_to_period_to_students[room]:
                room_to_period_to_students[room][period] += len(exams[exam_i].students)
            else:
                room_to_period_to_students[room][period] = len(exams[exam_i].students)
        else:
            room_to_period_to_students[room] = dict(period=len(exams[exam_i].students))
    for room_i, room_dict in room_to_period_to_students.items():
        for students in room_dict.values():
            violations += max(0, - rooms[room_i].capacity + students)
    return violations


def period_utilisation_constraint(schedule, exams, periods):
    """Returns penalty

    More time required in any schedule period than that available.
    """
    violations = 0
    for exam_i, (_, period_i) in enumerate(schedule):
        exam = exams[exam_i]
        period = periods[period_i]
        violations += exam.duration > period.duration
    return violations


def period_related_constraint(schedule, period_constraints):
    """Returns penalty

    Ordering requirements not obeyed.
    """
    violations = 0
    for order_constraint in period_constraints[PeriodHardEnum.AFTER]:
        first_period = schedule[order_constraint.first][1]
        second_period = schedule[order_constraint.second][1]
        violations += second_period >= first_period
    return violations


def room_related_constraint(schedule, room_constraints):
    """Returns penalty

    Room requirements not obeyed
    """
    violations = 0
    for constraint in room_constraints[RoomHardEnum.ROOM_EXCLUSIVE]:
        exam = constraint.first
        constraint_room, constraint_period = schedule[exam]
        for exam_i, (room, period) in enumerate(schedule):
            violations += constraint_room == room and constraint_period == period and exam != exam_i
    return violations

# Soft constraints
# After checking that all hard constraints are satisfied, the solution will be classified based on the satisfaction of the soft constraints. These are the following;


def get_period_to_exam_mapping(schedule, exams):
    period_to_exam = dict()
    for exam_i, (_, period_i) in enumerate(schedule):
        if period_i in period_to_exam:
            period_to_exam[period_i].append(exams[exam_i])
        else:
            period_to_exam[period_i] = [exams[exam_i]]
    return period_to_exam


def student_intersection(exams1, exams2):
    f_get_students = lambda x: x.students
    first_students = map(f_get_students, exams1)
    second_students = map(f_get_students, exams2)
    first_students = set([item for sublist in first_students for item in sublist])
    second_students = set([item for sublist in second_students for item in sublist])
    return first_students & second_students


def two_exams_in_a_row_constraint(schedule, periods, exams):
    """Returns penalty

    Count the number of occurrences where two examinations are taken by students straight after one another i.e. back to back. Once this has been established, the number of students involved in each occurance should be added and multiplied by the number provided in the �two in a row' weighting within the �Institutional Model Index'.
    """
    period_to_exam = get_period_to_exam_mapping(schedule, exams)
    periods_idx = range(len(periods))
    violations = 0
    for first_period, second_period in zip(periods_idx[:-1], periods_idx[1:]):
        if first_period in period_to_exam and second_period in period_to_exam \
                and periods[first_period].date == periods[second_period].date:
            intersect = student_intersection(period_to_exam[first_period], period_to_exam[second_period])
            violations += len(intersect)
    return violations


def two_exams_in_a_day_constraint(schedule, periods, exams):
    """Returns penalty

    In the case where there are three periods or more in a day, count the number of occurrences of students having two exams in a day which are not directly adjacent, i.e. not back to back, and multiply this by the ' two in a day' weighting provided within the 'Institutional Model Index'.
    """
    period_to_exam = get_period_to_exam_mapping(schedule, exams)
    used_periods = range(len(periods))
    violations = 0
    for first_period in range(len(periods)):
        for second_period in range(first_period+2, len(periods)):
            if periods[first_period].date == periods[second_period].date:
                intersect = student_intersection(period_to_exam[first_period], period_to_exam[second_period])
                violations += len(intersect)
    return violations


def period_spread_constraint(schedule, institutional_constraints):
    """Returns penalty

    This constraint allows an organisation to 'spread' an schedule's examinations over a specified number of periods. This can be thought of an extension of the two constraints previously described.  Within the �Institutional Model Index', a figure is provided relating to how many periods the solution should be �optimised' over.
    """
    return MUCH


def mixed_duration_constraint(schedule):
    """Returns penalty

    This applies a penalty to a ROOM and PERIOD (not Exam) where there are mixed durations.
    """
    return MUCH


def larger_exams_constraint(schedule, institutional_constraints):
    """Returns penalty

    It is desirable that examinations with the largest numbers of students are timetabled at the beginning of the examination session.
    """
    return MUCH


def room_penalty_constraint(schedule, institutional_constraints):
    """Returns penalty

    It is often the case that organisations want to keep certain room usage to a minimum. As with the 'Mixed Durations' component of the overall penalty, this part of the overall penalty should be calculated on a period by period basis. For each period, if a room used within the solution has an associated penalty, the penalty for that room for that period is calculated by multiplying the associated penalty by the number of times the room is used.
    """
    return MUCH


def period_penalty_constraint(schedule, institutional_constraints):
    """Returns penalty

    It is often the case that organisations want to keep certain period usage to a minimum. As with the 'Mixed Durations' and the 'Room Penalty' components of the overall penalty, this part of the overall penalty should be calculated on a period by period basis. For each period the penalty is calculated by multiplying the associated penalty by the number of times the exams timetabled within that period.
    """
    return MUCH

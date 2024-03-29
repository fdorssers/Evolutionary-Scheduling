import time

from institutionalconstraint import InstitutionalEnum
from misc import flatten, student_intersection
from individual import get_student_to_period_mapping, get_period_to_exam_mapping
from periodhardconstraint import PeriodHardEnum
from roomhardconstraint import RoomHardEnum

MUCH = 1000
times = [0.] * 13
previous = 0.


def timer(n, filter=0.99):
    global previous
    if n == 0:
        times[0] = time.time()
    if n > 0:
        duration = time.time() - previous
        times[n] = times[n] * filter + (1 - filter) * duration
    previous = time.time()


def naive_fitness(schedule, exams, periods, rooms, constraints):
    """
    Calculate the fitness of the schedule
    """
    room_con, period_con, institute_con = constraints
    soft_weightings = [institute_con[InstitutionalEnum.TWOINAROW][0].values[0],
                       institute_con[InstitutionalEnum.TWOINADAY][0].values[0],
                       institute_con[InstitutionalEnum.PERIODSPREAD][0].values[0],
                       institute_con[InstitutionalEnum.NONMIXEDDURATIONS][0].values[0],
                       institute_con[InstitutionalEnum.FRONTLOAD][0].values[0], -1, -1]

    exam_coincidence_fitness = exam_coincidence_constraint(schedule, period_con)
    period_exclusion_fitness = period_exclusion_constraint(schedule, period_con)
    room_occupancy_fitness = room_occupancy_constraint(schedule, exams, rooms)
    period_utilisation_fitness = period_utilisation_constraint(schedule, exams, periods)
    period_related_fitness = period_related_constraint(schedule, period_con)
    room_related_fitness = room_related_constraint(schedule, room_con)
    two_exams_in_a_row_fitness = two_exams_in_a_row_constraint(schedule, periods, exams)
    two_exams_in_a_day_fitness = two_exams_in_a_day_constraint(schedule, periods, exams)
    # period_spread_constraint4 is now fastest
    period_spread_fitness = period_spread_constraint4(schedule, exams, periods, institute_con)
    mixed_duration_fitness = mixed_duration_constraint(schedule, exams)
    larger_exams_fitness = larger_exams_constraint(schedule, exams, periods, institute_con)
    room_penalty_fitness = room_penalty_constraint(schedule, rooms)
    period_penalty_fitness = period_penalty_constraint(schedule, periods)

    hard_fitness = exam_coincidence_fitness + period_exclusion_fitness + room_occupancy_fitness + \
                   period_utilisation_fitness + period_related_fitness + room_related_fitness
    soft_values = [two_exams_in_a_row_fitness, two_exams_in_a_day_fitness, period_spread_fitness,
                   mixed_duration_fitness, larger_exams_fitness, room_penalty_fitness, period_penalty_fitness]
    soft_fitness = sum([weight * value for weight, value in zip(soft_weightings, soft_values)])
    return hard_fitness, soft_fitness


def hard_fitness_first(schedule, exams, periods, rooms, constraints):
    hard_fitness, soft_fitness = naive_fitness(schedule, exams, periods, rooms, constraints)
    return hard_fitness, soft_fitness


def soft_fitness_first(schedule, exams, periods, rooms, constraints):
    hard_fitness, soft_fitness = naive_fitness(schedule, exams, periods, rooms, constraints)
    return soft_fitness, hard_fitness

# Hard constraints

def exam_coincidence_constraint(schedule, period_con):
    """Returns penalty

    Two exams that should have same periods but don't.
    """
    exam_coincidence_constraints = period_con[PeriodHardEnum.EXAM_COINCIDENCE]
    violations = 0
    for exam_coincidence_constraint in exam_coincidence_constraints:
        first_exam = schedule[exam_coincidence_constraint.first]
        second_exam = schedule[exam_coincidence_constraint.second]
        violations += first_exam[1] != second_exam[1]
    return violations


def period_exclusion_constraint(schedule, period_con):
    """Returns penalty

    Two exams that shouldn't have same periods but don't.
    """
    exam_coincidence_constraints = period_con[PeriodHardEnum.EXCLUSION]
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


def period_related_constraint(schedule, period_con):
    """Returns penalty

    Ordering requirements not obeyed.
    """
    violations = 0
    for order_constraint in period_con[PeriodHardEnum.AFTER]:
        first_period = schedule[order_constraint.first][1]
        second_period = schedule[order_constraint.second][1]
        violations += second_period >= first_period
    return violations


def room_related_constraint(schedule, room_con):
    """Returns penalty

    Room requirements not obeyed
    """
    violations = 0
    for constraint in room_con[RoomHardEnum.ROOM_EXCLUSIVE]:
        exam = constraint.first
        constraint_room, constraint_period = schedule[exam]
        for exam_i, (room, period) in enumerate(schedule):
            violations += constraint_room == room and constraint_period == period and exam != exam_i
    return violations


# Soft constraints
# After checking that all hard constraints are satisfied, the solution will be classified based on the satisfaction 
# of the soft constraints. These are the following;

def two_exams_in_a_row_constraint(schedule, periods, exams):
    """Returns penalty

    Count the number of occurrences where two examinations are taken by students straight after one another i.e. back 
    to back. Once this has been established, the number of students involved in each occurance should be added and 
    multiplied by the number provided in the �two in a row' weighting within the �Institutional Model Index'.
    """
    period_to_exam = get_period_to_exam_mapping(schedule, exams, periods)
    periods_idx = range(len(periods))
    violations = 0
    for first_period, second_period in zip(periods_idx[:-1], periods_idx[1:]):
        if first_period in period_to_exam and second_period in period_to_exam and periods[first_period].date == periods[
            second_period].date:
            intersect = student_intersection(period_to_exam[first_period], period_to_exam[second_period])
            violations += len(intersect)
    return violations


def two_exams_in_a_day_constraint(schedule, periods, exams):
    """Returns penalty

    In the case where there are three periods or more in a day, count the number of occurrences of students having 
    two exams in a day which are not directly adjacent, i.e. not back to back, and multiply this by the ' two in a 
    day' weighting provided within the 'Institutional Model Index'.
    """
    period_to_exam = get_period_to_exam_mapping(schedule, exams, periods)
    violations = 0
    for first_period in range(len(periods)):
        for second_period in range(first_period + 2, len(periods)):
            if periods[first_period].date == periods[second_period].date:
                intersect = student_intersection(period_to_exam[first_period], period_to_exam[second_period])
                violations += len(intersect)
    return violations


def period_spread_constraint(schedule, exams, institute_con):
    """Returns penalty

    This constraint allows an organisation to 'spread' an schedule's examinations over a specified number of periods. 
    This can be thought of an extension of the two constraints previously described.  Within the �Institutional Model 
    Index', a figure is provided relating to how many periods the solution should be �optimised' over.
    """
    period_spread_constraints = institute_con[InstitutionalEnum.PERIODSPREAD]
    period_lengths = period_spread_constraints[0].values if len(period_spread_constraints) > 0 else []
    student_to_period = get_student_to_period_mapping(schedule, exams)
    violations = 0
    for period_length in period_lengths:
        for student, periods in student_to_period.items():
            periods = sorted(periods)
            for period_i, period in enumerate(periods):
                period_j = period_i + 1
                while len(periods) > period_j and periods[period_j] <= (period + period_length):
                    period_j += 1
                    violations += 1
    return violations


def period_spread_constraint2(schedule, exams, periods, institute_con):
    """Returns penalty

    This constraint allows an organisation to 'spread' an schedule's examinations over a specified number of periods. 
    This can be thought of an extension of the two constraints previously described.  Within the �Institutional Model 
    Index', a figure is provided relating to how many periods the solution should be �optimised' over.
    """
    period_spread_constraints = institute_con[InstitutionalEnum.PERIODSPREAD]
    period_lengths = period_spread_constraints[0].values if len(period_spread_constraints) > 0 else []
    period_to_exam = get_period_to_exam_mapping(schedule, exams, periods)
    period_to_students = dict()
    for period, exams in period_to_exam.items():
        period_to_students[period] = set(flatten(map(lambda exam: exam.students, exams)))
    periods = sorted(period_to_students.keys())
    violations = 0
    for period_length in period_lengths:
        for period_start in periods:
            for period_step in range(0, period_length - 1):
                period = period_start + period_step
                if period in period_to_students:
                    students_in_period = period_to_students[period]
                    other_periods = range(period + 1, period_start + period_length)
                    f_get_students = lambda p: period_to_students[p] if p in period_to_students else []
                    students_in_other_periods = set(flatten(map(f_get_students, other_periods)))
                    intersect = students_in_period & students_in_other_periods
                    violations += len(intersect)
    return violations


def period_spread_constraint3(schedule, exams, periods, institute_con):
    """Returns penalty

    This constraint allows an organisation to 'spread' an schedule's examinations over a specified number of periods. 
    This can be thought of an extension of the two constraints previously described.  Within the �Institutional Model 
    Index', a figure is provided relating to how many periods the solution should be �optimised' over.
    """
    period_spread_constraints = institute_con[InstitutionalEnum.PERIODSPREAD]
    period_lengths = period_spread_constraints[0].values if len(period_spread_constraints) > 0 else []
    period_to_exam = get_period_to_exam_mapping(schedule, exams, periods)
    period_to_students = dict()
    for period, exams in period_to_exam.items():
        period_to_students[period] = set(flatten(map(lambda exam: exam.students, exams)))
    periods = sorted(period_to_students.keys())
    violations = 0
    for period_length in period_lengths:
        for period_start in periods:
            cum_union = set()
            for window in range(period_start + period_length, period_start + 1, -1):
                period = period_start + window
                if period in period_to_students:
                    cum_union = cum_union | period_to_students[period]
                if (period - 1) in period_to_students:
                    students_in_period = period_to_students[period - 1]
                    intersect = students_in_period & cum_union
                    violations += len(intersect)
    return violations


def period_spread_constraint4(schedule, exams, periods, institute_con):
    violations = 0
    results = {i: set() for i, _ in enumerate(periods)}
    for e, (r, p) in enumerate(schedule):
        results[p].update(exams[e].students)

    spread = institute_con[InstitutionalEnum.PERIODSPREAD][0].values[0]
    for i in range(0, len(periods) - spread + 1):
        union = results[i]
        for j in range(i + 1, i + spread):
            temp = results[j]
            violations += len(union & temp)
            union.update(temp)

    return violations


def mixed_duration_constraint(schedule, exams):
    """Returns penalty

    This applies a penalty to a ROOM and PERIOD (not Exam) where there are mixed durations.
    """
    violations = 0
    result_dict = dict()
    # Create a mapping of rooms to periods to exams {room : {period : [i]}}
    for i, (r, p) in enumerate(schedule):
        if p in result_dict:
            if r in result_dict[p]:
                result_dict[p][r].append(i)
            else:
                result_dict[p][r] = [i]
        else:
            result_dict[p] = {r: [i]}

    for p, r_dict in result_dict.items():
        for r, i_list in result_dict[p].items():
            violations += len({exams[i].duration for i in i_list}) - 1

    return violations


def larger_exams_constraint(schedule, exams, periods, institute_con):
    """Returns penalty

    It is desirable that examinations with the largest numbers of students are timetabled at the beginning of the 
    examination session.
    """
    num_large_exams, num_large_periods, _ = institute_con[InstitutionalEnum.FRONTLOAD][0].values
    max_period = len(periods) - num_large_periods

    exam_sizes = dict(map(lambda kv: (kv[0], len(kv[1].students)), exams.items()))
    large_exams = reversed(sorted(range(len(exam_sizes)), key=lambda i: exam_sizes[i])[-num_large_exams:])

    violations = 0
    for large_exam in large_exams:
        violations += schedule[large_exam][1] > max_period

    return violations


def room_penalty_constraint(schedule, rooms):
    """Returns penalty

    It is often the case that organisations want to keep certain room usage to a minimum. As with the 'Mixed 
    Durations' component of the overall penalty, this part of the overall penalty should be calculated on a period by 
    period basis. For each period, if a room used within the solution has an associated penalty, the penalty for that 
    room for that period is calculated by multiplying the associated penalty by the number of times the room is used.
    """
    return sum([rooms[r].penalty for (r, _) in schedule])


def period_penalty_constraint(schedule, periods):
    """Returns penalty

    It is often the case that organisations want to keep certain period usage to a minimum. As with the 'Mixed 
    Durations' and the 'Room Penalty' components of the overall penalty, this part of the overall penalty should be 
    calculated on a period by period basis. For each period the penalty is calculated by multiplying the associated 
    penalty by the number of times the exams timetabled within that period.
    """
    return sum([periods[p].penalty for (_, p) in schedule])

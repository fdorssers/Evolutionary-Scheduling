MUCH = 1000


def naive_fitness(individual, period_constraints, room_constraints, institutional_constraints):
    """
    Calculate the fitness of the schedule
    """
    conflict_fitness = conflict_constraint(individual, period_constraints)
    room_occupancy_fitness = room_occupancy_constraint(individual, room_constraints)
    period_utilisation_fitness = period_utilisation_constraint(individual, period_constraints)
    period_related_fitness = period_related_constraint(individual, period_constraints)
    room_related_fitness = room_related_constraint(individual, room_constraints)
    two_exams_in_a_day_fitness = two_exams_in_a_day_constraint(individual)
    two_exams_in_a_row_fitness = two_exams_in_a_row_constraint(individual)
    period_spread_fitness = period_spread_constraint(individual, institutional_constraints)
    mixed_duration_fitness = mixed_duration_constraint(individual)
    larger_exams_fitness = larger_exams_constraint(individual, institutional_constraints)
    room_penalty_fitness = room_penalty_constraint(individual, institutional_constraints)
    period_penalty_fitness = period_penalty_constraint(individual, institutional_constraints)
    return (conflict_fitness, room_occupancy_fitness, period_utilisation_fitness, period_related_fitness, 
            period_utilisation_fitness, room_related_fitness, two_exams_in_a_row_fitness, two_exams_in_a_day_fitness, 
            period_spread_fitness, mixed_duration_fitness, larger_exams_fitness, room_penalty_fitness, 
            period_penalty_fitness)

# Hard constraints


def conflict_constraint(individual, period_constraints):
    """Returns penalty

    Two conflicting exams in the same period.
    """
    exam_coincidence_filter = lambda x: x.constraint == " EXAM_COINCIDENCE"
    exam_coincidence_constraints = list(filter(exam_coincidence_filter, period_constraints))
    violations = 0
    for exam_coincidence_constraint in exam_coincidence_constraints:
        first_exam = individual[exam_coincidence_constraint.first]
        second_exam = individual[exam_coincidence_constraint.second]
        violations += first_exam[1] == second_exam[1]
    if violations > 0:
        print(violations)
    return violations


def room_occupancy_constraint(individual, room_constraints):
    """Returns penalty

    More seating required in any individual period than that available.
    """
    return MUCH


def period_utilisation_constraint(individual, period_constraints):
    """Returns penalty

    More time required in any individual period than that available.
    """
    return MUCH


def period_related_constraint(individual, period_constraints):
    """Returns penalty

    Ordering requirements not obeyed.
    """
    return MUCH


def room_related_constraint(individual, room_constraints):
    """Returns penalty

    Room requirements not obeyed
    """
    return MUCH

# Soft constraints
# After checking that all hard constraints are satisfied, the solution will be classified based on the satisfaction of the soft constraints. These are the following;


def two_exams_in_a_row_constraint(individual):
    """Returns penalty

    Count the number of occurrences where two examinations are taken by students straight after one another i.e. back to back. Once this has been established, the number of students involved in each occurance should be added and multiplied by the number provided in the �two in a row' weighting within the �Institutional Model Index'.
    """
    return MUCH


def two_exams_in_a_day_constraint(individual):
    """Returns penalty

    In the case where there are three periods or more in a day, count the number of occurrences of students having two exams in a day which are not directly adjacent, i.e. not back to back, and multiply this by the ' two in a day' weighting provided within the 'Institutional Model Index'.
    """
    return MUCH


def period_spread_constraint(individual, institutional_constraints):
    """Returns penalty

    This constraint allows an organisation to 'spread' an individual's examinations over a specified number of periods. This can be thought of an extension of the two constraints previously described.  Within the �Institutional Model Index', a figure is provided relating to how many periods the solution should be �optimised' over.
    """
    return MUCH


def mixed_duration_constraint(individual):
    """Returns penalty

    This applies a penalty to a ROOM and PERIOD (not Exam) where there are mixed durations.
    """
    return MUCH


def larger_exams_constraint(individual, institutional_constraints):
    """Returns penalty

    It is desirable that examinations with the largest numbers of students are timetabled at the beginning of the examination session.
    """
    return MUCH


def room_penalty_constraint(individual, institutional_constraints):
    """Returns penalty

    It is often the case that organisations want to keep certain room usage to a minimum. As with the 'Mixed Durations' component of the overall penalty, this part of the overall penalty should be calculated on a period by period basis. For each period, if a room used within the solution has an associated penalty, the penalty for that room for that period is calculated by multiplying the associated penalty by the number of times the room is used.
    """
    return MUCH


def period_penalty_constraint(individual, institutional_constraints):
    """Returns penalty

    It is often the case that organisations want to keep certain period usage to a minimum. As with the 'Mixed Durations' and the 'Room Penalty' components of the overall penalty, this part of the overall penalty should be calculated on a period by period basis. For each period the penalty is calculated by multiplying the associated penalty by the number of times the exams timetabled within that period.
    """
    return MUCH

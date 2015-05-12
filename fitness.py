

def naive_fitness(individual):
    """
    Calculate the fitness of the schedule
    """
    rooms, periods = zip(*individual)
    return sum(rooms) + sum(periods),

# Hard constraints


def conflict_constraint(individual):
    """Returns penalty

    Two conflicting exams in the same period.
    """
    pass


def room_occupancy_constraint(individual):
    """Returns penalty

    More seating required in any individual period than that available.
    """
    pass


def period_utilisation_constraint(individual):
    """Returns penalty

    More time required in any individual period than that available.
    """
    pass


def period_related_constraint(individual):
    """Returns penalty

    Ordering requirements not obeyed.
    """
    pass


def room_related_constraint(individual):
    """Returns penalty

    Room requirements not obeyed
    """
    pass

# Soft constraints
# After checking that all hard constraints are satisfied, the solution will be classified based on the satisfaction of the soft constraints. These are the following;


def two_exams_in_a_row_constraint(individual):
    """Returns penalty

    Count the number of occurrences where two examinations are taken by students straight after one another i.e. back to back. Once this has been established, the number of students involved in each occurance should be added and multiplied by the number provided in the �two in a row' weighting within the �Institutional Model Index'.
    """
    pass


def two_exams_in_a_day_constraint(individual):
    """Returns penalty

    In the case where there are three periods or more in a day, count the number of occurrences of students having two exams in a day which are not directly adjacent, i.e. not back to back, and multiply this by the ' two in a day' weighting provided within the 'Institutional Model Index'.
    """
    pass


def period_spread_constraint(individual):
    """Returns penalty

    This constraint allows an organisation to 'spread' an individual's examinations over a specified number of periods. This can be thought of an extension of the two constraints previously described.  Within the �Institutional Model Index', a figure is provided relating to how many periods the solution should be �optimised' over.
    """
    pass


def mixed_duration_constraint(individual):
    """Returns penalty

    This applies a penalty to a ROOM and PERIOD (not Exam) where there are mixed durations.
    """
    pass


def larger_exams_constraint(individual):
    """Returns penalty

    It is desirable that examinations with the largest numbers of students are timetabled at the beginning of the examination session.
    """
    pass


def room_penalty_constraint(individual):
    """Returns penalty

    It is often the case that organisations want to keep certain room usage to a minimum. As with the 'Mixed Durations' component of the overall penalty, this part of the overall penalty should be calculated on a period by period basis. For each period, if a room used within the solution has an associated penalty, the penalty for that room for that period is calculated by multiplying the associated penalty by the number of times the room is used.
    """
    pass


def period_penalty_constraint(individual):
    """Returns penalty

    It is often the case that organisations want to keep certain period usage to a minimum. As with the 'Mixed Durations' and the 'Room Penalty' components of the overall penalty, this part of the overall penalty should be calculated on a period by period basis. For each period the penalty is calculated by multiplying the associated penalty by the number of times the exams timetabled within that period.
    """
    pass

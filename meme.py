from random import randint

from individual import get_period_to_room_to_exam_mapping


__author__ = 'pieter'


def mate_memes(exams, periods, rooms, institutional_constraints):
    def mate_memes_decorator(func):
        def wrapper(*args, **kargs):
            individual_a, individual_b = func(*args, **kargs)
            # room_limit_repair(individual_a, exams, rooms)
            # individual_a = frontload_repair(individual_a, exams, periods, institutional_constraints[InstitutionalEnum.FRONTLOAD][0])
            # individual_b = frontload_repair(individual_a, exams, periods, institutional_constraints[InstitutionalEnum.FRONTLOAD][0])
            return individual_a, individual_b
        return wrapper
    return mate_memes_decorator


def mutate_memes(func):
    def wrapper(*args, **kargs):
        individual = func(*args, **kargs)
        return individual
    return wrapper


def local_repair():
    pass


def frontload_repair(individual, exams, periods, frontload_constraint):
    number_exams = frontload_constraint.values[0]
    last_periods = frontload_constraint.values[1]
    initial_periods = len(periods) - last_periods
    largest_exams = sorted(range(0, len(exams)), key=lambda x: len(exams[x].students), reverse=True)[:number_exams]
    for exam_i in largest_exams:
        if individual[exam_i][1] >= initial_periods:
            individual[exam_i] = (individual[exam_i][0], randint(0, initial_periods - 1))
    return individual


def room_limit_repair(individual, exams, rooms):
    period_to_room_to_exam_mapping = get_period_to_room_to_exam_mapping(individual)
    leftover_exams = []
    leftover_room = dict()
    for period_i, room_to_exams_mapping in period_to_room_to_exam_mapping.items():
        # print('period_i: {}'.format(period_i))
        # print('room_to_exams: {}'.format(room_to_exams_mapping))
        for room_i, exam_is in room_to_exams_mapping.items():
            # print('Exams: {}'.format(exam_is))
            limit = rooms[room_i].capacity
            count = 0
            for exam_i in exam_is:
                count += len(exams[exam_i].students)
                print('Success')

            if count > limit:
                diff = count - limit
                print('{} students and only a capacity of {}'.format(count, limit))
                print('Exams: {}'.format(exam_is))
                print('Exams sizes: {}'.format(list(map(lambda x: len(exams[x].students), exam_is))))
    return
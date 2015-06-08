from random import randint

from individual import get_period_to_room_to_exam_mapping
from institutionalconstraint import InstitutionalEnum


__author__ = 'pieter'


def apply_memes(*args):
    def selection_wrapper(selection_func):
        def wrapper(population, k, tournsize):
            for i in range(len(population)):
                population[i] = individual_memes(population[i], *args)
            population = population_memes(population)
            pop = selection_func(population, k, tournsize)
            return pop

        return wrapper
    return selection_wrapper


def individual_memes(individual, exams, periods, rooms, institutional_constraints):
    # room_limit_repair(individual, exams, rooms)
    individual = frontload_repair(individual, exams, periods, institutional_constraints[InstitutionalEnum.FRONTLOAD][0])
    return individual


def population_memes(population):
    return population


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
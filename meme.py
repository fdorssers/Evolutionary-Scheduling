from random import randint, random, sample

import numpy as np

from individual import get_period_to_room_to_exam_mapping, get_student_to_period_to_exam_mapping
import individual
from institutionalconstraint import InstitutionalEnum
from periodhardconstraint import PeriodHardEnum

__author__ = 'pieter'

NUM_MEMES = 6


def individual_memes(individual, exams, periods, rooms, constraints, eatype):
    room_con, period_con, institute_con = constraints

    def memes(individual):

        meme_gene = individual.meme_gene
        meme_gene_len = len(meme_gene)
        meme_pb = meme_gene[:meme_gene_len / 2]
        meme_order = meme_gene[meme_gene_len / 2:]
        meme_order = np.argsort(meme_order)

        if eatype == 2 or eatype == 4:
            meme_pb = [1]*NUM_MEMES
        if eatype == 2 or eatype == 3:
            meme_order = range(0, NUM_MEMES)

        memes = [lambda indi: frontload_repair(indi, exams, periods, institute_con[InstitutionalEnum.FRONTLOAD][0], meme_pb[0]),
                 lambda indi: room_limit_naive(indi, exams, periods, rooms, meme_pb[1]),
                 lambda indi: exam_order_repair(indi, period_con, meme_pb[2]),
                 lambda indi: exam_coincidence_repair(indi, period_con, meme_pb[3]),
                 lambda indi: period_exclusion_repair(indi, len(periods), period_con, meme_pb[4]),
                 lambda indi: student_exam_coincidence_repair(indi, exams, periods, meme_pb[5])]
        for meme_i in meme_order:
            individual = memes[meme_i](individual)

        return individual

    if not hasattr(individual.fitness, "value"):
        return memes(individual)
    elif not individual.fitness.value:
        return memes(individual)
    else:
        return individual


def population_memes(population, indpb):
    """
    Population based memes should invalidate the fitness of the individuals that are changed
    :param population:
    :return:
    """
    population = remove_duplicates(population, indpb)
    return population


def student_exam_coincidence_repair(individual, exams, periods, pb=1.0):
    stpte = get_student_to_period_to_exam_mapping(individual, exams)
    exams_moved = set()
    all_periods = set(range(0, len(periods)))
    for student, pte in stpte.items():
        for period, exams in pte.items():
            for exam in exams[1:]:
                if exam not in exams_moved and random() < pb:
                    exams_moved.add(exam)
                    new_period = sample(all_periods - set(pte.keys()), 1)
                    individual[exam] = (individual[exam][0], new_period[0])
    return individual


def frontload_repair(individual, exams, periods, frontload_constraint, pb=1.0):
    number_exams = frontload_constraint.values[0]
    last_periods = frontload_constraint.values[1]
    initial_periods = len(periods) - last_periods
    if initial_periods > 0:
        largest_exams = sorted(range(0, len(exams)), key=lambda x: len(exams[x].students), reverse=True)[:number_exams]
        for exam_i in largest_exams:
            if individual[exam_i][1] >= initial_periods and random() < pb:
                individual[exam_i] = (individual[exam_i][0], randint(0, initial_periods - 1))
    return individual


def room_limit_naive(individual, exams, periods, rooms, pb=1.0):
    mapping = get_period_to_room_to_exam_mapping(individual)
    stack = []
    for _ in range(2):
        for period_i in range(len(periods)):
            for room_i in range(len(rooms)):
                total_students = 0
                # Remove exams from busy rooms
                if period_i in mapping and room_i in mapping[period_i] and random() < pb:
                    exam_list = mapping[period_i][room_i]
                    exam_sizes = list(map(lambda exam_i: len(exams[exam_i].students), exam_list))
                    total_students = sum(exam_sizes)
                    while total_students > rooms[room_i].capacity:
                        removed_exam = exam_list.pop()
                        removed_exam_size = len(exams[removed_exam].students)
                        total_students -= removed_exam_size
                        stack.append(removed_exam)
                # Add exams to empty rooms
                stack_remove = []
                for i in range(len(stack)):
                    if total_students + len(exams[stack[i]].students) < rooms[room_i].capacity:
                        added_exam = stack[i]
                        added_exam_size = len(exams[added_exam].students)
                        total_students += added_exam_size
                        individual[added_exam] = (room_i, period_i)
                        stack_remove.append(i)
                # Remove placed exams from stack
                for i in sorted(stack_remove, reverse=True):
                    del stack[i]

    return individual


def exam_order_repair(individual, period_constraints, pb=1.0):
    for constraint in period_constraints[PeriodHardEnum.AFTER]:
        if individual[constraint.first][1] < individual[constraint.second][1] and random() < pb:
            temp = individual[constraint.first]
            individual[constraint.first] = individual[constraint.second]
            individual[constraint.second] = temp
    return individual


def exam_coincidence_repair(individual, period_constraints, pb=1.0):
    exam_coincidence_constraints = period_constraints[PeriodHardEnum.EXAM_COINCIDENCE]
    for constraint in exam_coincidence_constraints:
        if individual[constraint.first][1] != individual[constraint.second][1] and random() < pb:
            if random() > 0.5:
                individual[constraint.first] = individual[constraint.first][0], individual[constraint.second][1]
            else:
                individual[constraint.second] = individual[constraint.second][0], individual[constraint.first][1]
    return individual


def period_exclusion_repair(individual, num_periods, period_constraints, pb=1.0):
    exam_coincidence_constraints = period_constraints[PeriodHardEnum.EXCLUSION]
    for constraint in exam_coincidence_constraints:
        if individual[constraint.first][1] == individual[constraint.second][1] and random() < pb:
            if random() > 0.5:
                individual[constraint.first] = individual[constraint.first][0], randint(0, num_periods - 1)
            else:
                individual[constraint.second] = individual[constraint.second][0], randint(0, num_periods - 1)
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


def remove_duplicates(population, indpb):
    individual_dict = dict()
    for indi_i, indi in enumerate(population):
        if indi not in individual_dict:
            individual_dict[indi] = True
        else:
            population[indi_i], = individual.mutate(indi, indpb)
            if hasattr(population[indi_i].fitness, "value"):
                del population[indi_i].fitness.value
    return population

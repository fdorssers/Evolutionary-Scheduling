import random

import numpy as np

__author__ = 'pieter'


class Individual(list):
    def __init__(self, func, num_rooms, num_periods):
        super().__init__(func())
        self.num_rooms = num_rooms
        self.num_periods = num_periods
        self.memepb = random.random() * 0.01

    def __hash__(self):
        return hash(str(list(self)))

    def __str__(self):
        room2period2exams = dict()
        str_size = np.zeros((self.num_rooms, self.num_periods), np.int)
        for exam_i, (room, period) in enumerate(self):
            str_size[room, period] += len(str(exam_i)) + 2
            if room in room2period2exams:
                if period in room2period2exams[room]:
                    room2period2exams[room][period].append(exam_i)
                else:
                    room2period2exams[room][period] = [exam_i]
            else:
                room2period2exams[room] = {period: [exam_i]}
        column_sizes = np.max(str_size, axis=0)
        column_sizes[column_sizes < 9] = 9
        ret = '         | '
        for period in range(self.num_periods):
            column_size = column_sizes[period]
            ret += ('period ' + str(period) + ' ' * column_size)[:column_size] + ' | '
        ret += '\n'
        for room in range(self.num_rooms):
            ret += '{:<9}'.format('room ' + str(room)) + '| '
            for period in range(self.num_periods):
                column_size = column_sizes[period]
                if room in room2period2exams and period in room2period2exams[room]:
                    ret += (str(room2period2exams[room][period]) + ' ' * column_size)[:column_size] + ' | '
                else:
                    ret += ' ' * column_size + ' | '
            ret += '\n'
        ret += 'memepb={}\n'.format(self.memepb)
        return ret


def exam_generator(num_rooms, num_periods):
    return random.randint(0, num_rooms - 1), random.randint(0, num_periods - 1)


def mutate(individual, indpb):
    """
    Mutate the schedule
    """
    if random.random() < indpb:
        individual.memepb = random.random()
    for i in range(0, len(individual)):
        if random.random() < indpb:
            new_room = random.randint(0, individual.num_rooms - 1)
            new_period = random.randint(0, individual.num_periods - 1)
            individual[i] = (new_room, new_period)
    return individual,


def cxTwoPoint(ind1, ind2):
    # Crossover meme probability
    if random.random() < .5:
        ind1.memepb = ind1.memepb
    else:
        ind2.memepb = ind1.memepb
    # Crossover schedule representation
    size = min(len(ind1), len(ind2))
    cxpoint1 = random.randint(1, size)
    cxpoint2 = random.randint(1, size - 1)
    if cxpoint2 >= cxpoint1:
        cxpoint2 += 1
    else:  # Swap the two cx points
        cxpoint1, cxpoint2 = cxpoint2, cxpoint1

    ind1[cxpoint1:cxpoint2], ind2[cxpoint1:cxpoint2] = ind2[cxpoint1:cxpoint2], ind1[cxpoint1:cxpoint2]

    return ind1, ind2


def get_student_to_period_mapping(schedule, exams):
    student_to_periods = dict()
    for exam_i, (_, period_i) in enumerate(schedule):
        for student in exams[exam_i].students:
            if student in student_to_periods:
                student_to_periods[student].add(period_i)
            else:
                student_to_periods[student] = {period_i}
    return student_to_periods


def get_student_to_period_to_exam_mapping(schedule, exams):
    stpte = dict()
    for exam_i, (_, period_i) in enumerate(schedule):
        for student in exams[exam_i].students:
            if student in stpte:
                if period_i in stpte[student]:
                    stpte[student][period_i].add(exam_i)
                else:
                    stpte[student][period_i] = [exam_i]
            else:
                stpte[student] = {period_i: exam_i}


def get_room_to_exam_mapping2(schedule, exams):
    room_to_exam = dict()
    for exam_i, (room_i, _) in enumerate(schedule):
        if room_i in room_to_exam:
            room_to_exam[room_i].append(exams[exam_i])
        else:
            room_to_exam[room_i] = [exams[exam_i]]
    return room_to_exam


def get_period_to_exam_mapping(schedule, exams):
    period_to_exam = dict()
    for exam_i, (_, period_i) in enumerate(schedule):
        if period_i in period_to_exam:
            period_to_exam[period_i].append(exams[exam_i])
        else:
            period_to_exam[period_i] = [exams[exam_i]]
    return period_to_exam


def get_room_to_exam_mapping(schedule, exams):
    room_to_exam = dict()
    for exam_i, (room_i, _) in enumerate(schedule):
        if room_i in room_to_exam:
            room_to_exam[room_i].append(exams[exam_i])
        else:
            room_to_exam[room_i] = [exams[exam_i]]
    return room_to_exam


def get_period_to_room_to_exam_mapping(schedule):
    period_to_room_to_exam_mapping = dict()
    for exam_i, (room_i, period_i) in enumerate(schedule):
        if period_i in period_to_room_to_exam_mapping:
            if room_i in period_to_room_to_exam_mapping[period_i]:
                period_to_room_to_exam_mapping[period_i][room_i].append(exam_i)
            else:
                period_to_room_to_exam_mapping[period_i][room_i] = [exam_i]
        else:
            period_to_room_to_exam_mapping[period_i] = dict()
            period_to_room_to_exam_mapping[period_i][room_i] = [exam_i]
    return period_to_room_to_exam_mapping

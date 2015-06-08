import random

import numpy as np


__author__ = 'pieter'


def exam_generator(num_rooms, num_periods):
    return random.randint(0, num_rooms - 1), random.randint(0, num_periods - 1)


def mutate(individual, indpb=0.05):
    """
    Mutate the schedule
    """
    for i in range(0, len(individual)):
        if random.random() < indpb:
            new_room = random.randint(0, individual.num_rooms - 1)
            new_period =  random.randint(0, individual.num_periods - 1)
            individual[i] = (new_room, new_period)
    return individual,


class Individual(list):
    def __init__(self, iterable, num_rooms, num_periods):
        super().__init__(iterable)
        self.num_rooms = num_rooms
        self.num_periods = num_periods

    def __hash__(self):
        return hash(str(self))

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
        ret = "         | "
        for period in range(self.num_periods):
            column_size = column_sizes[period]
            ret += ("period " + str(period) + " " * column_size)[:column_size] + " | "
        ret += "\n"
        for room in range(self.num_rooms):
            ret += "{:<9}".format("room " + str(room)) + "| "
            for period in range(self.num_periods):
                column_size = column_sizes[period]
                if room in room2period2exams and period in room2period2exams[room]:
                    ret += (str(room2period2exams[room][period]) + " " * column_size)[:column_size] + " | "
                else:
                    ret += " " * column_size + " | "
            ret += "\n"
        return ret
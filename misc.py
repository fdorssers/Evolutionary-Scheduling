import numpy as np

__author__ = 'pieter'


def flatten(list_of_lists):
    return [item for sublist in list_of_lists for item in sublist]


def schedule2string(schedule, max_rooms, max_periods):
    room2period2exams = dict()
    str_size = np.zeros((max_rooms, max_periods), np.int)
    for exam_i, (room, period) in enumerate(schedule):
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
    for period in range(max_periods):
        column_size = column_sizes[period]
        ret += ("period " + str(period) + " " * column_size)[:column_size] + " | "
    ret += "\n"
    for room in range(max_rooms):
        ret += "{:<9}".format("room " + str(room)) + "| "
        for period in range(max_periods):
            column_size = column_sizes[period]
            if room in room2period2exams and period in room2period2exams[room]:
                ret += (str(room2period2exams[room][period]) + " " * column_size)[:column_size] + " | "
            else:
                ret += " " * column_size + " | "
        ret += "\n"
    return ret
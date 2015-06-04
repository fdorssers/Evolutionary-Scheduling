from threading import Lock
import os

import numpy as np
import matplotlib.pyplot as plt


__author__ = 'pieter'

lock = Lock()



def flatten(list_of_lists):
    """
    Flattens a list of lists
    :param list_of_lists:
    :type list_of_lists: list of list
    :return: flattened list
    :rtype: list
    """
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


def create_dictionary(dir):
    with lock:
        if not os.path.exists(dir):
            os.makedirs(dir)


def plot_ea_progress(logbook, parameter_str):
    duration, best, worst, average = logbook.select("duration", "best", "worst", "avg")
    plt.plot(duration, best)
    plt.plot(duration, worst)
    plt.plot(duration, average)
    plt.xlabel("Generation")
    plt.ylabel("Fitness")
    plt.suptitle("Fitness vs. duration")
    plt.title(parameter_str)
    plt.legend(["best", "worst", "average"])
    num_xs = min(len(duration), 15)
    xs = np.round(np.linspace(0, len(duration) - 1, num_xs)).astype(np.int).tolist()
    plt.xticks([duration[x] for x in xs], xs)
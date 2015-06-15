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


def create_directory(dir):
    with lock:
        if not os.path.exists(dir):
            os.makedirs(dir)


def dict_add(dict, key, value):
    if key in dict:
        dict[key] += value
    else:
        dict[key] = value


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


def student_intersection(exams1, exams2):
    f_get_students = lambda x: x.students
    first_students = map(f_get_students, exams1)
    second_students = map(f_get_students, exams2)
    first_students = set([item for sublist in first_students for item in sublist])
    second_students = set([item for sublist in second_students for item in sublist])
    return first_students & second_students

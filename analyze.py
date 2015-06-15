import matplotlib
matplotlib.use('Agg')

import json
import os
import pickle
import zipfile
import binascii
from deap import creator
import individual
from deap import base
import numpy as np
from misc import dict_add, create_directory

__author__ = 'pieter'


def set_creator(name):
    fitness_name = "FitnessMin_" + str(name)
    individual_name = "Individual_" + str(name)
    creator.create(fitness_name, base.Fitness, weights=(-1, -1))
    creator.create(individual_name, individual.Individual, fitness=getattr(creator, fitness_name))


def read_log(filename):
    zip_file = zipfile.ZipFile(filename, 'r')
    info = json.loads(zip_file.read("logbook/info.json").decode())
    set_creator(info["ea"]["name"])
    logbook = pickle.load(zip_file.open("logbook/raw.bin"))
    population = pickle.load(zip_file.open("pop/complete.bin"))
    hof = pickle.load(zip_file.open("pop/hof.bin"))
    zip_file.close()
    return info, logbook, population, hof


def best_fitness_values(hofs):
    return np.array([hof[0].fitness.wvalues for hof in hofs])


def all_fitness_values(pops):
    return np.array([indi.fitness.wvalues for pop in pops for indi in pop])


def mean_memes(pops):
    return np.array([indi.meme_gene for pop in pops for indi in pop])


def best_memes(hofs):
    return np.array([hof[0].meme_gene for hof in hofs])


def plot_fitness(x, y, title, xlabel, ylabel):
    matplotlib.pyplot.clf()
    matplotlib.pyplot.plot(np.array(x).T, np.array(y).T)
    matplotlib.pyplot.title(title)
    matplotlib.pyplot.xlabel(xlabel)
    matplotlib.pyplot.ylabel(ylabel)


def bar_memes(x, y1, y2, title, meme_names):
    matplotlib.pyplot.clf()
    matplotlib.pyplot.title(title)
    matplotlib.pyplot.xlabel('Meme')
    matplotlib.pyplot.ylabel('Value')
    matplotlib.pyplot.bar(x, y1, width=0.4)
    matplotlib.pyplot.bar(x+.5, y2, width=0.4, color='g')
    matplotlib.pyplot.xticks(np.arange(0,6)+0.5, meme_names, rotation=15)
    matplotlib.pyplot.legend(['hof', 'pop'])

def data_info_vs_fitness(dir, filter, info_key):
    hofs = dict()
    pops = dict()
    for file in os.listdir(dir):
        filename = os.path.join(dir, file)
        if filter(filename):
            info, logbook, population, hof = read_log(filename)
            dict_add(hofs, info["ea"][info_key], [hof])
            dict_add(pops, info["ea"][info_key], [population])
    keys = list(sorted(hofs.keys()))
    best_values = list(map(lambda k: best_fitness_values(hofs[k]), keys))
    all_values = list(map(lambda k: all_fitness_values(pops[k]), keys))
    f_mean = lambda x: np.mean(x, 0)
    mean_best_values = np.array(list(map(f_mean, best_values)))
    mean_all_values = np.array(list(map(f_mean, all_values)))
    return np.array([keys, keys]), np.array([mean_best_values[:, 0], mean_all_values[:, 0]]), np.array([mean_best_values[:, 1], mean_all_values[:, 1]])


def data_memes(dir, filter):
    hofs = []
    pops = []
    for file in os.listdir(dir):
        filename = os.path.join(dir, file)
        if filter(filename):
            info, logbook, population, hof = read_log(filename)
            hofs.append(hof)
            pops.append(population)
    hof_memes = best_memes(hofs)
    pop_memes = mean_memes(pops)
    create_directory('analyze')
    meme_names = ['front_load', 'room_limit', 'exam_order', 'exam_coincidence', 'period_exclusion', 'student_exam']
    bar_memes(np.arange(0, 6), np.mean(hof_memes[:, :6], 0), np.mean(pop_memes[:, :6], 0), 'Average meme probability', meme_names)
    matplotlib.pyplot.savefig('analyze/meme_pb')
    bar_memes(np.arange(0, 6), np.mean(hof_memes[:, 6:], 0), np.mean(pop_memes[:, 6:], 0), 'Average meme order', meme_names)
    matplotlib.pyplot.savefig('analyze/meme_order')


def info_vs_fitness(dir, filter):
    for info in ['indi', 'cxpb', 'mutpb', 'gen']:
        xs, ys_hard, ys_soft = data_info_vs_fitness(dir, filter, info)
        create_directory('analyze')
        plot_fitness(xs, ys_hard, "Hard constraint fitness vs {}".format(info), info, "Avg fitness")
        matplotlib.pyplot.savefig('analyze/hard_vs_{}'.format(info))
        plot_fitness(xs, ys_soft, "Soft constraint fitness vs {}".format(info), info, "Avg fitness")
        matplotlib.pyplot.savefig('analyze/soft_vs_{}'.format(info))


dir = "logs"
filter = lambda filename: True # "2015_06_14" in filename

info_vs_fitness(dir, filter)
data_memes(dir, filter)
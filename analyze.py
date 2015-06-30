import matplotlib

# matplotlib.use('Agg')

import json
import os
import pickle
import zipfile
from deap import creator
import individual
from deap import base
import numpy as np
from misc import dict_add, create_directory
import seaborn

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
    ret = np.array([hof[0].fitness.wvalues for hof in hofs])
    return ret


def mean_fitness_values(pops):
    ret = []
    for pop in pops:
        ret.append(np.mean([indi.fitness.wvalues for indi in pop], 0))
    return ret


def mean_memes(pops):
    return np.array([indi.meme_gene for pop in pops for indi in pop])


def best_memes(hofs):
    return np.array([hof[0].meme_gene for hof in hofs])


def plot_fitness(x, y1, y2, title, xlabel, ylabel, continuous=True):
    matplotlib.pyplot.clf()
    marker = '-' if continuous else 'o'
    matplotlib.pyplot.plot(np.array(x).T, np.array(y1).T, marker, ms=15)
    matplotlib.pyplot.plot(np.array(x).T, np.array(y2).T, marker, ms=15)
    matplotlib.pyplot.title(title)
    matplotlib.pyplot.xlabel(xlabel)
    matplotlib.pyplot.ylabel(ylabel)
    matplotlib.pyplot.legend(["Best", "Mean"], loc='lower right')

    if xlabel == 'EA type':
        matplotlib.pyplot.xticks(x, ['Default', '1st MA', '2nd MA prob', '2nd MA order', '2nd MA both'])

def bar_memes(x, y1, y2, title, meme_names):
    matplotlib.pyplot.clf()
    matplotlib.pyplot.title(title)
    matplotlib.pyplot.xlabel('Meme')
    matplotlib.pyplot.ylabel('Value')
    matplotlib.pyplot.bar(x, y1, width=0.4)
    matplotlib.pyplot.bar(x + .5, y2, width=0.4, color='g')
    matplotlib.pyplot.xticks(np.arange(0, 6) + 0.5, meme_names, rotation=15)
    matplotlib.pyplot.legend(['hof', 'pop'])


def data_info_vs_fitness(dir, filter, info_key):
    hofs = dict()
    pops = dict()
    for file in os.listdir(dir):
        filename = os.path.join(dir, file)
        if filter(filename):
            print("Getting info data from {}".format(filename))
            info, logbook, population, hof = read_log(filename)
            info["ea"]["set"] = filename[filename.find('_set=')+5:filename.find('_set=')+6]
            dict_add(hofs, info["ea"][info_key], [hof])
            dict_add(pops, info["ea"][info_key], [population])
    keys = list(sorted(hofs.keys()))
    best_values = list(map(lambda k: best_fitness_values(hofs[k]), keys))
    all_values = list(map(lambda k: mean_fitness_values(pops[k]), keys))
    f_mean = lambda x: np.mean(x, 0)
    mean_best_values = np.array(list(map(f_mean, best_values)))
    mean_all_values = np.array(list(map(f_mean, all_values)))
    return np.array(keys), mean_best_values[:, 0], mean_all_values[:, 0], mean_best_values[:, 1], mean_all_values[:, 1]


def data_memes(dir, filter):
    hofs = []
    pops = []
    for file in os.listdir(dir):
        filename = os.path.join(dir, file)
        if filter(filename):
            print("Getting meme data from {}".format(filename))
            info, logbook, population, hof = read_log(filename)
            hofs.append(hof)
            pops.append(population)
    hof_memes = best_memes(hofs)
    pop_memes = mean_memes(pops)
    meme_names = ['front_load', 'room_limit', 'exam_order', 'exam_coincidence', 'period_exclusion', 'student_exam']
    bar_memes(np.arange(0, 6), np.mean(hof_memes[:, :6], 0), np.mean(pop_memes[:, :6], 0), 'Average meme probability',
              meme_names)
    matplotlib.pyplot.savefig('analyze/meme_pb')
    bar_memes(np.arange(0, 6), np.mean(hof_memes[:, 6:], 0), np.mean(pop_memes[:, 6:], 0), 'Average meme order',
              meme_names)
    matplotlib.pyplot.savefig('analyze/meme_order')


def info_vs_fitness(dir, filter):
    names = {'indi': 'Individuals', 'cxpb': 'Crossover probability', 'mutpb':'Mutation probability', 'gen':'Generations', 'eatype':'EA type', 'set': 'Dataset'}
    for info in ['set']: #['eatype', 'indi', 'cxpb', 'mutpb', 'gen']:
        xs, ys_hard_best, ys_hard_mean, ys_soft_best, ys_soft_mean = data_info_vs_fitness(dir, filter, info)
        create_directory('analyze')
        plot_fitness(xs, ys_hard_best, ys_hard_mean, "Hard constraint fitness vs {}".format(names[info]), names[info], "Avg fitness", continuous=info not in ['eatype', 'set'])
        matplotlib.pyplot.savefig('analyze/hard_vs_{}'.format(info))
        plot_fitness(xs, ys_soft_best, ys_soft_mean, "Soft constraint fitness vs {}".format(names[info]), names[info], "Avg fitness", continuous=info not in ['eatype', 'set'])
        matplotlib.pyplot.savefig('analyze/soft_vs_{}'.format(info))


def analyze_single_meme(filename):
    _, logbook, _, _ = read_log(filename)
    memes = np.array(logbook.chapters['memepb'].select('mean'))
    matplotlib.pyplot.figure()
    matplotlib.pyplot.title('Probability of applying meme')
    matplotlib.pyplot.plot(memes[:, :6])
    matplotlib.pyplot.legend(['LargerExam', 'RoomRelated', 'PeriodRelated', 'Exam coincidence', 'Exam exclusion', 'Student coincidence'])
    matplotlib.pyplot.savefig('analyze/single_meme_pb')
    matplotlib.pyplot.figure()
    matplotlib.pyplot.title('Order of applying meme')
    matplotlib.pyplot.plot(memes[:, 6:])
    matplotlib.pyplot.legend(['LargerExam', 'RoomRelated', 'PeriodRelated', 'Exam coincidence', 'Exam exclusion', 'Student coincidence'])
    matplotlib.pyplot.savefig('analyze/single_meme_order')


def analyze_single_progress(filename):
    _, logbook, _, _ = read_log(filename)
    means = np.array(logbook.chapters['hard'].select('avg'))
    matplotlib.pyplot.figure()
    matplotlib.pyplot.title('Average hard constraint violations')
    matplotlib.pyplot.plot(means)
    matplotlib.pyplot.xlabel("Generation")
    matplotlib.pyplot.ylabel("Fitness")
    matplotlib.pyplot.savefig('analyze/progress')



dir = "logs"
filter = lambda filename: "exp_type" in filename

# info_vs_fitness(dir, filter)
# data_memes(dir, filter)
filename = 'logs/ea_2015_06_15_18_36_50_name=exp_type_ind=1000_gen=100_set=1_cpb=0.5_mpb=0.15_eatype=5_rep=0_2437.zip'
analyze_single_meme(filename)
analyze_single_progress(filename)
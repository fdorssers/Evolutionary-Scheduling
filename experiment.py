from copy import deepcopy
import threading
import matplotlib
import argparse

matplotlib.use("Agg")

from queue import Queue, Empty
import os
import pickle
import random
import sys
import datetime
import time
import zipfile

from misc import plot_ea_progress, create_directory
from scheduling_ea import SchedulingEA
import schedule_parser_2 as parser

__author__ = 'pieter'

q = Queue()


def main(individuals=[10], generations=[3], crossover_pb=[0.5], mutation_pb=[0.2], dataset=[1], experiment_name='NA', init_ea_file=None, eatype=[3]):

    datasets = list(["data/exam_comp_set{}.exam".format(ds) for ds in dataset])

    eas = []

    for dataset in datasets:
        info = parser.parse(dataset)
        for num_individual in individuals:
            for num_generations in generations:
                for cxpb in crossover_pb:
                    for mutpb in mutation_pb:
                        for eat in eatype:
                            if init_ea_file is None:
                                rand = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                                ea_name = "ea_{}".format(rand)
                            else:
                                # Get the original name of the ea
                                ea_name = os.path.split(init_ea_file)[-1][:-9]
                            print("Starting {} with {} individuals, {} generations, {} ea type, {} crossover probability and {} mutation "
                                  "probability on {}".format(ea_name, num_individual, num_generations, eat, cxpb, mutpb, dataset))
                            ea2 = SchedulingEA(*info, name=ea_name, indi=num_individual, gen=num_generations, indpb=0.1,
                                               tournsize=3, cxpb=cxpb, mutpb=mutpb, eatype=eat, save_callback=save_fun)
                            ea2.save_name = ea2.name + '_name={}_ind={}_gen={}_set={}_cpb={}_mpb={}_eatype={}'.format(experiment_name, num_individual, num_generations, dataset[18:19], cxpb, mutpb, eat) + '_' + str(random.randint(1000, 9999)).zfill(4)
                            if init_ea_file is not None:
                                pop, ea2.hof = load_population(init_ea_file)
                                ea2.pop = (pop + ea2.pop)[:num_individual]

                            ea2.start()
                            eas.append(ea2)
                            time.sleep(1)

    while len(eas) > 0:
        for i, ea in enumerate(eas):
            if ea.done:
                save_data(ea, ea.pop, ea.logbook)
                del eas[i]
                break
        try:
            ea, pop, logbook = q.get(False)
            if not ea.done and (not hasattr(ea, 'last_save') or ea.last_save + 1000. < time.time()):
                save_data(ea, pop, deepcopy(logbook))
                ea.last_save = time.time()
            q.task_done()
        except Empty:
            pass


def save_fun(ea):
    def save_me(pop, logbook):
        q.put((ea, pop, logbook))

    return save_me


def load_population(file_name):
    def load_pickle(zip, name):
        pickled = zip.open(name)
        return pickle.load(pickled)

    zip_file = zipfile.ZipFile(file_name)
    ret = load_pickle(zip_file, "pop/complete.bin"), load_pickle(zip_file, "pop/hof.bin")
    zip_file.close()
    return ret


def save_data(ea, pop, logbook):
    def temp_file(name):
        return os.path.join(log_dir, str(random.randint(0, 10 ** 10)) + name)

    def write_to_zip_and_remove(temp, path):
        zip_file.write(temp, path)
        os.remove(temp)

    def pickle_save_zip(data, folder, file):
        temp = temp_file(file)
        path = os.path.join(folder, file)
        f = open(temp, 'wb')
        pickle.dump(data, f)
        f.close()
        write_to_zip_and_remove(temp, path)

    def save_str(object, folder, file):
        temp = temp_file(file)
        path = os.path.join(folder, file)
        f = open(temp, 'w')
        f.write(str(object))
        f.close()
        write_to_zip_and_remove(temp, path)

    def save_readable_population(pop, folder, file):
        path = os.path.join(folder, file)
        temp = temp_file(file)
        f = open(temp, 'w')
        pop = sorted(pop, key=lambda x: x.fitness, reverse=True)
        for i, ind in enumerate(pop):
            f.write("Fitness = {}\n".format(ind.fitness.wvalues))
            f.write(str(ind))
            f.write("===\n\n")
        f.close()
        write_to_zip_and_remove(temp, path)

    def plot_progress(logbook, parameters, folder, file):
        matplotlib.pyplot.clf()
        path = os.path.join(folder, file)
        temp = temp_file(file)
        parameter_str = ", ".join([str(k) + '$=' + str(parameters[k]) + '$' for k in sorted(parameters)])
        plot_ea_progress(logbook, parameter_str)
        matplotlib.pyplot.savefig(temp)
        write_to_zip_and_remove(temp, path)

    # Save
    print("Saving {}".format(ea.save_name))
    log_dir = "logs"
    create_directory(log_dir)
    name = str(ea.save_name).replace(" ", "_")
    zip_file = zipfile.ZipFile(os.path.join(log_dir, name + ".zip"), 'w', zipfile.ZIP_DEFLATED)
    pickle_save_zip(logbook, "logbook", "raw.bin")
    pickle_save_zip(pop, "pop", "complete.bin")
    pickle_save_zip(ea.hof, "pop", "hof.bin")
    save_str(logbook, "logbook", "show.txt")
    save_str(str(ea), "logbook", "info.json")
    save_readable_population(pop, "pop", "show.txt")
    plot_progress(logbook.chapters["hard"], ea.jsonify()["ea"], "pop", "plot_hard.png")
    plot_progress(logbook.chapters["soft"], ea.jsonify()["ea"], "pop", "plot_soft.png")
    zip_file.close()
    print("Done saving {}".format(ea.save_name))


if __name__ == "__main__":
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('-p', '--population', type=int, nargs='+', help='size of population', required=False)
    argument_parser.add_argument('-g', '--generation', type=int, nargs='+', help='number of generations', required=False)
    argument_parser.add_argument('-c', '--crossover', type=float, nargs='+', help='crossover probability', required=False)
    argument_parser.add_argument('-m', '--mutation', type=float, nargs='+', help='mutation probability', required=False)
    argument_parser.add_argument('-s', '--setnumber', type=int, nargs='+', help='number of the dataset', required=False)
    argument_parser.add_argument('-e', '--eatype', type=int, nargs='+', help='type of evolutionary algorithm (1=standard, 2=meme, 3=probablistic memes, 4=probabilistic meme order, 5=probabilistic memes and order)', required=False)
    argument_parser.add_argument('-b', '--batchname', help='name of the batch', required=False)
    argument_parser.add_argument('-i', '--initfile', help='file from previous run', required=False)
    args = argument_parser.parse_args()

    params = dict()
    if args.population:
        params['individuals'] = args.population
    if args.generation:
        params['generations'] = args.generation
    if args.crossover:
        params['crossover_pb'] = args.crossover
    if args.mutation:
        params['mutation_pb'] = args.mutation
    if args.setnumber:
        params['dataset'] = args.setnumber
    if args.eatype:
        params['eatype'] = args.eatype
    if args.batchname:
        params['experiment_name'] = args.batchname
    if args.initfile:
        params['init_ea_file'] = args.initfile

    main(**params)
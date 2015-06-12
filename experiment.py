from queue import Queue, Empty
import os
import pickle
import random
import sys
import datetime
import time
import zipfile

import matplotlib.pyplot as plt

from misc import plot_ea_progress, create_directory
from scheduling_ea import SchedulingEA
import schedule_parser_2 as parser


__author__ = 'pieter'

q = Queue()


def main(individuals=100, generations=50, crossover_pb=0.5, mutation_pb=0.2, init_ea_file=None):
    # Parse possible commandline arguments

    def parse_list_or_number(param, type):
        try:
            return [type(param)]
        except ValueError:
            return list(map(type, param.split(",")))

    individuals = parse_list_or_number(individuals, int)
    generations = parse_list_or_number(generations, int)
    crossover_pb = parse_list_or_number(crossover_pb, float)
    mutation_pb = parse_list_or_number(mutation_pb, float)

    random.seed(64)
    info = parser.parse()
    eas = []

    for num_individual in individuals:
        for num_generations in generations:
            for cxpb in crossover_pb:
                for mutpb in mutation_pb:
                    if init_ea_file is None:
                        rand = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
                        ea_name = "ea_{}".format(rand)
                    else:
                        ea_name = os.path.split(init_ea_file)[-1][:-4]
                    print("Starting {} with {} individuals, {} generations, {} crossover probability and {} mutation "
                          "probability".format(ea_name, num_individual, num_generations, cxpb, mutpb))
                    ea2 = SchedulingEA(*info, name=ea_name, indi=num_individual, gen=num_generations, indpb=0.1,
                                       tournsize=3, cxpb=cxpb, mutpb=mutpb, save_callback=save_fun)
                    if init_ea_file is not None:
                        ea2.pop, ea2.hof = load_population(init_ea_file)
                        ea2.name += '-'
                    ea2.start()
                    eas.append(ea2)

    while len(eas) > 0:
        try:
            ea, pop, logbook = q.get(False)
            save_data(ea, pop, logbook)
        except Empty:
            for i, ea in enumerate(eas):
                if ea.done:
                    save_data(ea, ea.pop, ea.logbook, always_save=True)
                    del eas[i]
                    break


def save_fun(ea):
    def save_me(pop, logbook):
        q.put((ea, pop, logbook))
    return save_me


def load_population(file_name):
    def load_pickle(zip, name):
        pickled = zip.open(name)
        return pickle.load(pickled)

    zip_file = zipfile.ZipFile(file_name)
    return load_pickle(zip_file, "pop/complete.bin"), load_pickle(zip_file, "pop/hof.bin")


def save_data(ea, pop, logbook, always_save=False):
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

    def save_readable_population(pop, num_rooms, num_periods, folder, file):
        path = os.path.join(folder, file)
        temp = temp_file(file)
        f = open(temp, 'w')
        pop = sorted(pop, key=lambda x: sum(x.fitness.wvalues), reverse=True)
        for i, ind in enumerate(pop):
            fitt_comp = "(" + ") + (".join(
                map(lambda x: "*".join(map(str, x)), zip(ind.fitness.weights, ind.fitness.values))) + ")"
            f.write("Fitness {} = {}\n".format(sum(ind.fitness.wvalues), fitt_comp))
            f.write(str(ind))
            f.write("===\n\n")
        f.close()
        write_to_zip_and_remove(temp, path)

    def plot_progress(logbook, parameters, folder, file):
        plt.clf()
        path = os.path.join(folder, file)
        temp = temp_file(file)
        parameter_str = ", ".join([str(k) + '$=' + str(parameters[k]) + '$' for k in sorted(parameters)])
        plot_ea_progress(logbook, parameter_str)
        plt.savefig(temp)
        write_to_zip_and_remove(temp, path)

    # Save
    if not hasattr(ea, 'last_save') or ea.last_save + 1000. < time.time() or always_save:
        ea.last_save = time.time()
        print("Saving {}".format(ea.name))
        log_dir = "logs"
        create_directory(log_dir)
        name = str(ea.name).replace(" ", "_")
        zip_file = zipfile.ZipFile(os.path.join(log_dir, name + ".zip"), 'w', zipfile.ZIP_DEFLATED)
        pickle_save_zip(logbook, "logbook", "raw.bin")
        pickle_save_zip(pop, "pop", "complete.bin")
        pickle_save_zip(ea.hof, "pop", "hof.bin")
        save_str(logbook, "logbook", "show.txt")
        save_str(str(ea), "logbook", "info.json")
        save_readable_population(pop, ea.num_rooms, ea.num_periods, "pop", "show.txt")
        if ea.logbook is not None:
            plot_progress(logbook, ea.jsonify()["ea"], "pop", "plot.png")
        zip_file.close()
        print("Done saving {}".format(ea.name))


if __name__ == "__main__":
    main(*sys.argv[1:])
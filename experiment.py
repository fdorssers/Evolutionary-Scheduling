import matplotlib
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


def main(individuals=50, generations=50, crossover_pb=0.5, mutation_pb=0.2, init_ea_file=None):
    # Parse possible commandline arguments

    def parse_list_or_number(param, type):
        try:
            return [type(param)]
        except ValueError:
            return list(map(type, param.split(",")))

    # init_ea_file = 'logs/ea_2015_06_12_17_45_00_7696.zip'

    individuals = parse_list_or_number(individuals, int)
    generations = parse_list_or_number(generations, int)
    crossover_pb = parse_list_or_number(crossover_pb, float)
    mutation_pb = parse_list_or_number(mutation_pb, float)

    info = parser.parse()
    eas = []

    for num_individual in individuals:
        for num_generations in generations:
            for cxpb in crossover_pb:
                for mutpb in mutation_pb:
                    if init_ea_file is None:
                        rand = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
                        ea_name = "ea_{}".format(rand)
                    else:
                        # Get the original name of the ea
                        ea_name = os.path.split(init_ea_file)[-1][:-9]
                    print("Starting {} with {} individuals, {} generations, {} crossover probability and {} mutation "
                          "probability".format(ea_name, num_individual, num_generations, cxpb, mutpb))
                    ea2 = SchedulingEA(*info, name=ea_name, indi=num_individual, gen=num_generations, indpb=0.1,
                                       tournsize=3, cxpb=cxpb, mutpb=mutpb, save_callback=save_fun)
                    ea2.save_name = ea2.name + '_' + str(random.randint(1000, 9999)).zfill(4)
                    if init_ea_file is not None:
                        pop, ea2.hof = load_population(init_ea_file)
                        ea2.pop = (pop + ea2.pop)[:num_individual]

                    ea2.start()
                    eas.append(ea2)

    while len(eas) > 0:
        try:
            ea, pop, logbook = q.get(False)
            if not hasattr(ea, 'last_save') or ea.last_save + 1000. < time.time():
                save_data(ea, pop, logbook)
                ea.last_save = time.time()
            q.task_done()
        except Empty:
            for i, ea in enumerate(eas):
                if ea.done:
                    save_data(ea, ea.pop, ea.logbook)
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
        start = time.time()
        path = os.path.join(folder, file)
        f = open(temp, 'w')
        f.write(str(object))
        f.close()
        write_to_zip_and_remove(temp, path)

    def save_readable_population(pop, folder, file):
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
    indi_logbook = logbook.chapters['individual']
    pickle_save_zip(indi_logbook, "logbook", "raw.bin")
    pickle_save_zip(pop, "pop", "complete.bin")
    pickle_save_zip(ea.hof, "pop", "hof.bin")
    save_str(indi_logbook, "logbook", "show.txt")
    save_str(str(ea), "logbook", "info.json")
    save_readable_population(pop, "pop", "show.txt")
    if ea.logbook is not None:
        plot_progress(indi_logbook, ea.jsonify()["ea"], "pop", "plot.png")
    zip_file.close()
    print("Done saving {}".format(ea.name))


if __name__ == "__main__":
    main(*sys.argv[1:])
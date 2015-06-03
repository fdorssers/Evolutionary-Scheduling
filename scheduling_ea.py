import multiprocessing
import pickle
import random
import threading

from deap import base
from deap import creator
from deap import tools
from deap import algorithms
import numpy as np

import fitness
from institutionalconstraint import InstitutionalEnum
from misc import schedule2string, create_dictionary








# Todo: use deap wrapper to set bounds on rooms and periods indexes


class SchedulingEA(threading.Thread):
    def __init__(self, exams, periods, rooms, period_constraints, room_constraints, institutional_constraints, name,
                 individuals, generations, indpb=0.05, tournsize=3, cxpb=0.5, mutpb=0.1):
        super().__init__()
        # Problem properties
        self.exams = exams
        self.periods = periods
        self.rooms = rooms
        self.period_con = period_constraints
        self.room_con = room_constraints
        self.institutional_con = institutional_constraints
        self.num_rooms = len(rooms)
        self.num_periods = len(periods)
        self.num_exams = len(exams)
        # EA properties
        self.individuals = individuals
        self.generations = generations
        self.indpb = indpb
        self.tournsize = tournsize
        self.cxpb = cxpb
        self.mutpb = mutpb

        self.name = name
        self.fitness_name = "FitnessMin_" + str(self.name)
        self.individual_name = "Individual_" + str(self.name)
        self.toolbox = None
        self.logbook = None
        self.pop = None
        self.hof = None
        self.stats = None

        self.init_create_types()
        self.init_toolbox()
        self.init_population()
        self.init_stats()

        pool = multiprocessing.Pool()
        self.toolbox.register("map", pool.map)

    def init_create_types(self):
        soft_weightings = [-self.institutional_con[InstitutionalEnum.TWOINAROW][0].values[0],
                           -self.institutional_con[InstitutionalEnum.TWOINADAY][0].values[0],
                           -self.institutional_con[InstitutionalEnum.PERIODSPREAD][0].values[0],
                           -self.institutional_con[InstitutionalEnum.NONMIXEDDURATIONS][0].values[0],
                           -self.institutional_con[InstitutionalEnum.FRONTLOAD][0].values[0], -1, -1]
        creator.create(self.fitness_name, base.Fitness, weights=tuple([-100.0] * 5 + soft_weightings))
        creator.create(self.individual_name, list, fitness=getattr(creator, self.fitness_name))

    def init_toolbox(self):
        # Use the self.toolbox to initialize the individuals
        self.toolbox = base.Toolbox()
        # Attributes to generate random rooms and periods
        self.toolbox.register("attr_exam",
                              lambda: (random.randint(0, self.num_rooms - 1), random.randint(0, self.num_periods - 1)))
        # Create the individual with alternating rooms and periods
        self.toolbox.register("individual", tools.initRepeat, getattr(creator, self.individual_name),
                              self.toolbox.attr_exam, n=self.num_exams)
        # Create the population as a list of the individuals
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        # Use the fitness function specified in this file
        self.toolbox.register("evaluate", fitness.naive_fitness, exams=self.exams, periods=self.periods,
                              rooms=self.rooms, period_constraints=self.period_con, room_constraints=self.room_con,
                              institutional_constraints=self.institutional_con)
        # Use two point cross over
        self.toolbox.register("mate", tools.cxTwoPoint)
        # Use the mutation operator specified in this file
        self.toolbox.register("mutate", self.mutate, indpb=self.indpb)
        # Use tournament selection
        self.toolbox.register("select", tools.selTournament, tournsize=self.tournsize)

    def init_population(self):
        self.pop = self.toolbox.population(n=self.individuals)
        self.hof = tools.HallOfFame(5, similar=np.array_equal)

    def init_stats(self):
        stats = tools.Statistics(lambda pop: pop.fitness.wvalues)
        stats.register("name", lambda x: self.name)
        stats.register("avg", np.mean)
        stats.register("std", np.std)
        stats.register("min", np.min)
        stats.register("max", np.max)

        # stats2 = tools.Statistics()
        # stats2.register("best", lambda x: "\n" + schedule2string(self.hof[0], self.num_rooms, self.num_periods))
        # self.mstats = tools.MultiStatistics(fitness=stats, size=stats2)
        self.stats = stats

    def run(self):
        self.pop, self.logbook = algorithms.eaSimple(self.pop, self.toolbox, cxpb=self.cxpb, mutpb=self.mutpb,
                                                     ngen=self.generations, stats=self.stats, halloffame=self.hof)
        self.save()

    def mutate(self, individual, indpb=0.05):
        """
        Mutate the schedule
        """
        for i in range(0, len(individual)):
            if random.random() < indpb:
                individual[i] = (
                    random.randint(0, self.num_rooms - 1), (individual[i][1] + random.randint(-2, 2)) % self.num_periods
                )
        return individual,

    def save(self):
        def pickle_save(data, folder):
            create_dictionary(folder)
            f = open(folder + filename + ".bin", 'wb')
            pickle.dump(data, f)
            f.close()

        filename = str(self.name).replace(" ", "_")
        raw_folder = "logbook/raw/"
        show_folder = "logbook/show/"
        complete_pop_folder = "pop/complete/"
        hof_pop_folder = "pop/hof/"
        show_pop_folder = "pop/show/"
        # binaries
        pickle_save(self.logbook, raw_folder)
        pickle_save(self.pop, complete_pop_folder)
        pickle_save(self.hof, hof_pop_folder)
        # txt
        create_dictionary(show_folder)
        f = open(show_folder + filename + ".txt", 'w')
        f.write(str(self.logbook))
        f.close()

        create_dictionary(show_pop_folder)
        f = open(show_pop_folder + filename + ".txt", 'w')
        pop = sorted(self.pop, key=lambda x: sum(x.fitness.wvalues), reverse=True)
        for i, ind in enumerate(pop):
            fitt_comp = "(" + ") + (".join(
                map(lambda x: "*".join(map(str, x)), zip(ind.fitness.weights, ind.fitness.values))) + ")"
            f.write("Fitness {} = {}\n".format(sum(ind.fitness.wvalues), fitt_comp))
            f.write(schedule2string(ind, self.num_rooms, self.num_periods))
            f.write("===\n\n")
        f.close()

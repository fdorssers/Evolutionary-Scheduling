import multiprocessing
import threading
import json
import time

from deap import base

from deap import creator

from deap import tools
import numpy as np

from customalgorithms import ea_custom
import fitness
import individual
from institutionalconstraint import InstitutionalEnum
import meme


class SchedulingEA(threading.Thread):
    def __init__(self, exams, periods, rooms, period_constraints, room_constraints, institutional_constraints, name,
                 indi, gen, indpb=0.05, tournsize=3, cxpb=0.5, mutpb=0.1, memepb=.25, save_callback=None):
        super().__init__()

        # Problem properties
        self.exams = exams
        self.periods = periods
        self.rooms = rooms
        self.constraints = (room_constraints, period_constraints, institutional_constraints)
        self.num_rooms = len(rooms)
        self.num_periods = len(periods)
        self.num_exams = len(exams)
        self.soft_weightings = [-self.constraints[2][InstitutionalEnum.TWOINAROW][0].values[0],
                           -self.constraints[2][InstitutionalEnum.TWOINADAY][0].values[0],
                           -self.constraints[2][InstitutionalEnum.PERIODSPREAD][0].values[0],
                           -self.constraints[2][InstitutionalEnum.NONMIXEDDURATIONS][0].values[0],
                           -self.constraints[2][InstitutionalEnum.FRONTLOAD][0].values[0], -1, -1]

        # EA properties
        self.indi = indi
        self.gen = gen
        self.indpb = indpb
        self.tournsize = tournsize
        self.cxpb = cxpb
        self.mutpb = mutpb
        self.memepb = memepb

        # Constants
        self.name = name
        self.fitness_name = "FitnessMin_" + str(self.name)
        self.individual_name = "Individual_" + str(self.name)
        self.toolbox = None
        self.logbook = None
        self.pop = None
        self.hof = None
        self.stats = None

        self.done = False
        self.save_callback = save_callback

        self.init_create_types()
        self.init_toolbox()
        self.init_population()
        self.init_stats()

        pool = multiprocessing.Pool()
        self.toolbox.register("map", pool.map)

    def init_create_types(self):
        creator.create(self.fitness_name, base.Fitness, weights=tuple([-100.0] * 6 + self.soft_weightings))
        creator.create(self.individual_name, individual.Individual, fitness=getattr(creator, self.fitness_name))

    def init_toolbox(self):
        # Use the self.toolbox to initialize the individuals
        self.toolbox = base.Toolbox()
        # Generator of room-period combinations
        self.toolbox.register("exam", individual.exam_generator, self.num_rooms, self.num_periods)
        # Generator of schedules
        self.toolbox.register("schedule", tools.initRepeat, list, self.toolbox.exam, n=self.num_exams)
        # Generator of Individuals; schedule + constants
        self.toolbox.register("individual", getattr(creator, self.individual_name), self.toolbox.schedule,
                              self.num_rooms, self.num_periods)
        # Create the population as a list of the individuals
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)

        # Use the fitness function specified in this file
        self.toolbox.register("evaluate", fitness.naive_fitness, exams=self.exams, periods=self.periods,
                              rooms=self.rooms, constraints=self.constraints)
        # Use two point cross over
        self.toolbox.register("mate", individual.cxTwoPoint)
        # Use the mutation operator specified in this file
        self.toolbox.register("mutate", individual.mutate, indpb=self.indpb)
        # self.toolbox.decorate("mutate", meme.mutate_memes)
        # Use tournament selection
        self.toolbox.register("select", tools.selTournament, tournsize=self.tournsize)
        # Use individual memes
        self.toolbox.register("individual_meme", meme.individual_memes, exams=self.exams, periods=self.periods,
                              rooms=self.rooms, constraints=self.constraints)
        # Use population memes
        self.toolbox.register("population_meme", meme.population_memes, indpb=self.indpb)
        # Save data every iteration
        if self.save_callback is not None:
            self.toolbox.register("iteration_callback", self.save_callback(self))

    def init_population(self):
        self.pop = self.toolbox.population(n=self.indi)
        self.hof = tools.HallOfFame(5, similar=np.array_equal)

    def init_stats(self):
        start = time.time()
        pop_stats = tools.Statistics(lambda indi: np.sum(indi.fitness.wvalues, 0))
        pop_stats.register("name", lambda x: self.name)
        pop_stats.register("avg", np.mean)
        pop_stats.register("std", np.std)
        pop_stats.register("worst", np.min)
        pop_stats.register("best", np.max)
        pop_stats.register("duration", lambda x: time.time() - start)

        indi_stats = tools.Statistics(lambda indi: indi.memepb)
        indi_stats.register("mean", np.mean)
        indi_stats.register("std", np.std)

        self.stats = tools.MultiStatistics(individual=pop_stats, memepb=indi_stats)

    def run(self):
        self.pop, self.logbook = ea_custom(self.pop, self.toolbox, cxpb=self.cxpb, mutpb=self.mutpb, ngen=self.gen,
                                           stats=self.stats, halloffame=self.hof)
        self.done = True

    def jsonify(self):
        return {"problem": {"exams": self.num_exams, "periods": self.num_periods, "rooms": self.num_rooms,
                            "period_con": len(self.constraints[1]), "room_con": len(self.constraints[0]),
                            "institutional_con": len(self.constraints[2])},
                "ea": {"indi": self.indi, "gen": self.gen, "cxpb": self.cxpb, "indpb": self.indpb, "mutbp": self.mutpb,
                       "tournsize": self.tournsize}}

    def __str__(self):
        return json.dumps(self.jsonify(), sort_keys=True)

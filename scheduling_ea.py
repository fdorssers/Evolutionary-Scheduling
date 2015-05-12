import random

import numpy as np
from deap import algorithms
from deap import base
from deap import creator
from deap import tools
import schedule_parser as parser
import fitness


def mutate(individual, indpb=0.05):
    """
    Mutate the schedule
    """
    for i in range(0, len(individual)):
        individual[i] = (random.randint(0, ROOMS), individual[i][1] + random.randint(-2, 2))
    return individual,


exams, periods, rooms, period_constraints, room_constraints, institutional_constraints = parser.parse()
ROOMS = len(rooms)
PERIODS = len(periods)
EXAMS = len(exams)
INDIVIDUALS = 10

print("Running ea with", ROOMS, "rooms,", PERIODS, "periods and", EXAMS, "exams")

# Use 12 fitness functions with equal weight
creator.create("FitnessMin", base.Fitness, weights=tuple([-1.0] * 12))
# Set the type of individuals to lists
creator.create("Individual", list, fitness=creator.FitnessMin)

# Use the toolbox to initialize the individuals
toolbox = base.Toolbox()
# Attributes to generate random rooms and periods
toolbox.register("attr_exam", lambda: (random.randint(0, ROOMS), random.randint(0, PERIODS)))
# Create the individual with alternating rooms and periods
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_exam, n=EXAMS)
# Create the population as a list of the individuals
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Use the fitness function specified in this file
toolbox.register("evaluate", fitness.naive_fitness, period_constraints=period_constraints, room_constraints=room_constraints,
                 institutional_constraints=institutional_constraints)
# Use two point cross over
toolbox.register("mate", tools.cxTwoPoint)
# Use the mutation operator specified in this file
toolbox.register("mutate", mutate, indpb=0.05)
# Use tournament selection
toolbox.register("select", tools.selTournament, tournsize=3)


def main():
    random.seed(64)

    # Create population with fixed size
    pop = toolbox.population(n=300)

    # Numpy equality function (operators.eq) between two arrays returns the
    # equality element wise, which raises an exception in the if similar()
    # check of the hall of fame. Using a different equality function like
    # numpy.array_equal or numpy.allclose solve this issue.
    hof = tools.HallOfFame(5, similar=np.array_equal)

    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)

    algorithms.eaSimple(pop, toolbox, cxpb=0.5, mutpb=0.01, ngen=40, stats=stats, halloffame=hof)

    return pop, stats, hof


if __name__ == "__main__":
    main()

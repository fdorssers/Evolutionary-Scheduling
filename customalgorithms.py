from deap.algorithms import varAnd
from deap import tools
import random


def ea_custom(population, toolbox, cxpb, mutpb, ngen, eatype, stats=None, halloffame=None, verbose=__debug__,
              iteration_callback=None):
    """This algorithm reproduce the simplest evolutionary algorithm as
    presented in chapter 7 of [Back2000]_.

    :param population: A list of individuals.
    :param toolbox: A :class:`~deap.base.Toolbox` that contains the evolution
                    operators.
    :param cxpb: The probability of mating two individuals.
    :param mutpb: The probability of mutating an individual.
    :param ngen: The number of generation.
    :param stats: A :class:`~deap.tools.Statistics` object that is updated
                  inplace, optional.
    :param halloffame: A :class:`~deap.tools.HallOfFame` object that will
                       contain the best individuals, optional.
    :param verbose: Whether or not to log the statistics.
    :returns: The final population.

    It uses :math:`\lambda = \kappa = \mu` and goes as follow.
    It first initializes the population (:math:`P(0)`) by evaluating
    every individual presenting an invalid fitness. Then, it enters the
    evolution loop that begins by the selection of the :math:`P(g+1)`
    population. Then the crossover operator is applied on a proportion of
    :math:`P(g+1)` according to the *cxpb* probability, the resulting and the
    untouched individuals are placed in :math:`P'(g+1)`. Thereafter, a
    proportion of :math:`P'(g+1)`, determined by *mutpb*, is
    mutated and placed in :math:`P''(g+1)`, the untouched individuals are
    transferred :math:`P''(g+1)`. Finally, those new individuals are evaluated
    and the evolution loop continues until *ngen* generations are completed.
    Briefly, the operators are applied in the following order ::

        evaluate(population)
        for i in range(ngen):
            offspring = select(population)
            offspring = mate(offspring)
            offspring = mutate(offspring)
            evaluate(offspring)
            population = offspring

    This function expects :meth:`toolbox.mate`, :meth:`toolbox.mutate`,
    :meth:`toolbox.select` and :meth:`toolbox.evaluate` aliases to be
    registered in the toolbox.

    .. [Back2000] Back, Fogel and Michalewicz, "Evolutionary Computation 1 :
       Basic Algorithms and Operators", 2000.
    """
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    if eatype != 1:
        if hasattr(toolbox, 'individual_meme'):
            population = list(toolbox.map(toolbox.individual_meme, population))
        if hasattr(toolbox, 'population_meme'):
            population = toolbox.population_meme(population)

    # Evaluate the individuals with an invalid fitness
    # invalid_ind = [ind for ind in population if not ind.fitness.valid]

    fitnesses = toolbox.map(toolbox.evaluate, population)
    # fitnesses = toolbox.map(toolbox.evaluate_hard, population)
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit

    if halloffame is not None:
        halloffame.update(population)

    record = stats.compile(population) if stats else {}
    logbook.record(gen=0, nevals=len(population), **record)
    if verbose:
        print(logbook.stream)

    # Begin the generational process
    for gen in range(1, ngen + 1):
        # Select the next generation individuals
        # offspring = toolbox.select(population, len(population))
        if gen % 2 == 1:
            offspring = toolbox.select_soft(population, len(population))
        else:
            offspring = toolbox.select_hard(population, len(population))

        # Vary the pool of individuals
        offspring = varAnd(offspring, toolbox, cxpb, mutpb)

        if eatype != 1:
            if hasattr(toolbox, 'individual_meme'):
                offspring = list(toolbox.map(toolbox.individual_meme, offspring))
            if hasattr(toolbox, 'population_meme'):
                offspring = toolbox.population_meme(offspring)

        # Evaluate the individuals with an invalid fitness
        # invalid_ind = [ind for ind in offspring if not ind.fitness.valid]

        # Evaluate all individuals
        fitnesses = toolbox.map(toolbox.evaluate, offspring)
        # if gen % 2 == 1:
        #     fitnesses = toolbox.map(toolbox.evaluate_soft, offspring)
        # else:
        #     fitnesses = toolbox.map(toolbox.evaluate_hard, offspring)
        for ind, fit in zip(offspring, fitnesses):
            ind.fitness.values = fit

        # Update the hall of fame with the generated individuals
        if halloffame is not None:
            halloffame.update(offspring)

        # Replace the current population by the offspring
        population[:] = offspring

        # Append the current generation statistics to the logbook
        record = stats.compile(population) if stats else {}
        logbook.record(gen=gen, nevals=len(offspring), **record)
        if verbose:
            print(logbook.stream)

        if hasattr(toolbox, 'iteration_callback'):
            toolbox.iteration_callback(population, logbook)

    return population, logbook


def selRandom(individuals, k):
    """Select *k* individuals at random from the input *individuals* with
    replacement. The list returned contains references to the input
    *individuals*.

    :param individuals: A list of individuals to select from.
    :param k: The number of individuals to select.
    :returns: A list of selected individuals.

    This function uses the :func:`~random.choice` function from the
    python base :mod:`random` module.
    """
    return [random.choice(individuals) for i in range(k)]


def selTournament(individuals, k, tournsize):
    """Select *k* individuals from the input *individuals* using *k*
    tournaments of *tournsize* individuals. The list returned contains
    references to the input *individuals*.

    :param individuals: A list of individuals to select from.
    :param k: The number of individuals to select.
    :param tournsize: The number of individuals participating in each tournament.
    :returns: A list of selected individuals.

    This function uses the :func:`~random.choice` function from the python base
    :mod:`random` module.
    """
    chosen = []
    for i in range(k):
        aspirants = selRandom(individuals, tournsize)
        chosen.append(max(aspirants, key=attrgetter("fitness")))
    return chosen


def selTournamentHard(individuals, k, tournsize):
    chosen = []
    fgh = fitnessgetter(hard_first=True)
    for i in range(k):
        aspirants = selRandom(individuals, tournsize)
        chosen.append(max(aspirants, key=fgh))
    return chosen


def selTournamentSoft(individuals, k, tournsize):
    chosen = []
    fgs = fitnessgetter(hard_first=False)
    for i in range(k):
        aspirants = selRandom(individuals, tournsize)
        chosen.append(max(aspirants, key=fgs))
    return chosen


class fitnessgetter:
    def __init__(self, hard_first=True):
        if hard_first:
            def func(obj):
                return obj.fitness.wvalues
            self._call = func
        else:
            def func(obj):
                return obj.fitness.wvalues[::-1]
            self._call = func

    def __call__(self, obj):
        return self._call(obj)


class attrgetter:
    """
    Return a callable object that fetches the given attribute(s) from its operand.
    After f = attrgetter('name'), the call f(r) returns r.name.
    After g = attrgetter('name', 'date'), the call g(r) returns (r.name, r.date).
    After h = attrgetter('name.first', 'name.last'), the call h(r) returns
    (r.name.first, r.name.last).
    """
    def __init__(self, attr, *attrs):
        if not attrs:
            if not isinstance(attr, str):
                raise TypeError('attribute name must be a string')
            names = attr.split('.')

            def func(obj):
                for name in names:
                    obj = getattr(obj, name)
                return obj
            self._call = func
        else:
            getters = tuple(map(attrgetter, (attr,) + attrs))

            def func(obj):
                return tuple(getter(obj) for getter in getters)
            self._call = func

    def __call__(self, obj):
        return self._call(obj)
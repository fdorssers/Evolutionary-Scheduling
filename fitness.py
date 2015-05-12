

def naive_fitness(individual):
    """
    Calculate the fitness of the schedule
    """
    rooms, periods = zip(*individual)
    return sum(rooms) + sum(periods),

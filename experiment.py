import random
import sys

from scheduling_ea import SchedulingEA
import schedule_parser_2 as parser


__author__ = 'pieter'


def main(individuals=50, generations=100):
    # Parse possible commandline arguments
    try:
        individuals = [int(individuals)]
    except ValueError:
        individuals = map(int, individuals.split(","))
    try:
        generations = [int(generations)]
    except:
        generations = map(int, generations.split(","))

    random.seed(64)
    info = parser.parse()

    for num_individual in individuals:
        for num_generations in generations:
            ea2 = SchedulingEA(*info, name="ea_initial_{}_{}".format(num_individual, num_generations),
                               individuals=num_individual, generations=num_generations, indpb=0.1, tournsize=3)
            ea2.start()


if __name__ == "__main__":
    print(sys.argv)

    main(*sys.argv[1:])
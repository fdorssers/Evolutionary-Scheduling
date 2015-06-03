import random
import sys
import time

from scheduling_ea import SchedulingEA
import schedule_parser_2 as parser


__author__ = 'pieter'


def main(individuals=10, generations=10, crossover_pb=0.5, mutation_pb=0.1):
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

    for num_individual in individuals:
        for num_generations in generations:
            for cxpb in crossover_pb:
                for mutpb in mutation_pb:
                    rand = round(time.time() * 1000)
                    ea_name = "ea_initial_{}".format(rand)
                    print("Starting {} with {} individuals, {} generations, {} crossover probability and {} mutation "
                          "probability".format(ea_name, num_individual, num_generations, cxpb, mutpb))
                    ea2 = SchedulingEA(*info, name=ea_name, indi=num_individual, gen=num_generations,
                                       indpb=0.1, tournsize=3, cxpb=cxpb, mutpb=mutpb)
                    ea2.start()


if __name__ == "__main__":
    main(*sys.argv[1:])
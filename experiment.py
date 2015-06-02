import random
import sys
from scheduling_ea import SchedulingEA
import schedule_parser_2 as parser

__author__ = 'pieter'


def main(individuals=50, generations=100):
    # Parse possible commandline arguments
    individuals = int(individuals)
    generations = int(generations)
    
    random.seed(64)
    info = parser.parse()

    ea2 = SchedulingEA(*info, name="ea_initial_" + str(individuals), individuals=individuals, generations=generations)
    ea2.start()

if __name__ == "__main__":
    main(*sys.argv[1:])
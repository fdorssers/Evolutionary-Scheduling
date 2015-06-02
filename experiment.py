import random
from scheduling_ea import SchedulingEA
import schedule_parser_2 as parser

__author__ = 'pieter'


def main():
    random.seed(64)
    info = parser.parse()

    for indi in range(500, 1500, 100):
        ea2 = SchedulingEA(*info, name="ea_initial_" + str(indi), individuals=indi, generations=1000)
        ea2.start()

if __name__ == "__main__":
    main()
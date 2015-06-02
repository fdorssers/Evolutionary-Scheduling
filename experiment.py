import random
from scheduling_ea import SchedulingEA
import schedule_parser_2 as parser

__author__ = 'pieter'


def main():
    random.seed(64)
    info = parser.parse()

    for i in range(2):
        ea2 = SchedulingEA(*info, name="ea {}".format(i), individuals=20, generations=5)
        ea2.start()

if __name__ == "__main__":
    main()
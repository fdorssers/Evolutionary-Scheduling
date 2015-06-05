__author__ = 'pieter'



def mate_memes(func):
    def wrapper(*args, **kargs):
        individual_a, individual_b = func(*args, **kargs)
        return individual_a, individual_b
    return wrapper


def mutate_memes(func):
    def wrapper(*args, **kargs):
        individual = func(*args, **kargs)
        return individual
    return wrapper


def local_repair():
    pass
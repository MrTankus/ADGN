import itertools
import numpy as np


def sum_square_connectivity_componenet_fitness_function(network):
    return sum(map(lambda cc: len(cc) ** 2, network.graph.get_connectivity_components()))


def avg_on_paths_length_fitness_function(network):
    sensors = filter(lambda vertex: not vertex.get('is_relay'), network.graph.vertices)
    sensors_pairs = itertools.combinations(sensors, 2)
    path_distances = [network.graph.get_path_length(v1, v2) for v1, v2 in sensors_pairs]
    finite_paths = list(filter(lambda d: d != np.inf, path_distances))
    number_of_finit_paths = len(finite_paths)
    sum_path_distances = sum(finite_paths)
    if number_of_finit_paths:
        number_of_vertices = len(network.graph.vertices)
        return sum_path_distances / (number_of_vertices * (number_of_vertices - 1))
    return 0


def harmonic_avg_on_paths_length_fitness_function(network):
    sensors = filter(lambda node: not node.get('is_relay'), network.graph.vertices)
    sensors_pairs = itertools.combinations(sensors, 2)
    path_distances = [network.graph.get_path_length(v1, v2) for v1, v2 in sensors_pairs]
    finite_paths = list(filter(lambda d: d != np.inf, path_distances))
    path_distances = list(map(lambda d: 1/d, finite_paths))
    sum_path_distances = sum(path_distances)
    if sum_path_distances:
        return float(len(path_distances) / sum_path_distances)
    return 0


def robustness_fitness_function(network):
    return 0


class FitnessFunctions(object):

    SUM_SQUARE_CC_SIZE = 1
    AVG_PATH_LENGTH = 2
    HARMONIC_AVG_PATH_LENGTH = 3
    ROBUSTNESS = 4

    mapping = {
        SUM_SQUARE_CC_SIZE: sum_square_connectivity_componenet_fitness_function,
        AVG_PATH_LENGTH: avg_on_paths_length_fitness_function,
        HARMONIC_AVG_PATH_LENGTH: harmonic_avg_on_paths_length_fitness_function,
        ROBUSTNESS: robustness_fitness_function
    }

    @staticmethod
    def get_fitness_function(ff):
        return FitnessFunctions.mapping.get(ff)




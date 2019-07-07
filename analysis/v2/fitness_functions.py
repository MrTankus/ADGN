import itertools
from scipy.special import comb


def sum_square_connectivity_componenet_fitness_function(network):
    return sum(map(lambda cc: len(cc) ** 2, network.graph.get_connectivity_components()))


def harmonic_avg_on_paths_length_fitness_function(network):
    n = len(network.graph.vertices)
    total_combinations = comb(n, 2)
    distance_sum = list()
    ccs = network.graph.get_connectivity_components()
    if len(ccs) == n:
        return 0

    for cc in network.graph.get_connectivity_components():
        if len(cc) == 1:
            continue
        sensors = filter(lambda vertex: not vertex.get('is_relay'), cc)
        sensors_pairs = itertools.combinations(sensors, 2)
        path_distances = [network.graph.get_path_length(v1, v2) for v1, v2 in sensors_pairs]
        distance_sum.append(sum(map(lambda d: 1.0/d, path_distances)))
        total_combinations -= len(path_distances)

    return ((n * (n-1)) / 2) / sum(distance_sum)


class Optimum(object):
    MIN = 0
    MAX = 1


class FitnessFunctions(object):

    SUM_SQUARE_CC_SIZE = 1
    HARMONIC_AVG_PATH_LENGTH = 3

    mapping = {
        SUM_SQUARE_CC_SIZE: (sum_square_connectivity_componenet_fitness_function, Optimum.MAX),
        HARMONIC_AVG_PATH_LENGTH: (harmonic_avg_on_paths_length_fitness_function, Optimum.MIN),
    }

    @staticmethod
    def get_fitness_function(ff):
        ff_info = FitnessFunctions.mapping.get(ff)
        if ff_info:
            return ff_info[0]
        return None

    @staticmethod
    def get_fitness_function_optimum(ff):
        ff_info = FitnessFunctions.mapping.get(ff)
        if ff_info:
            return ff_info[1]
        return None

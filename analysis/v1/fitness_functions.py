import itertools


def sum_square_connectivity_componenet_fitness_function(network):
    connectivity_components = network.graph.get_connectivity_components()
    return sum([len(cc) ** 2 for cc in connectivity_components])


def avg_on_paths_length_fitness_function(network):
    sensors = filter(lambda node: not node.get('is_relay'), network.graph.nodes.values())
    sensors_pairs = itertools.combinations(sensors, 2)
    paths = list(filter(bool, [network.graph.get_path(n1, n2) for (n1, n2) in sensors_pairs]))
    path_distances = list(map(len, paths))
    sum_path_distances = sum(path_distances)
    if len(path_distances):
        return sum_path_distances / len(path_distances)
    return 0


def harmonic_avg_on_paths_length_fitness_function(network):
    sensors = filter(lambda node: not node.get('is_relay'), network.graph.nodes.values())
    sensors_pairs = itertools.combinations(sensors, 2)
    paths = list(filter(bool, [network.graph.get_path(n1, n2) for (n1, n2) in sensors_pairs]))
    path_distances = list(map(lambda l: 1/l, map(len, paths)))
    sum_path_distances = sum(path_distances)
    if sum_path_distances:
        return len(path_distances) / sum_path_distances
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




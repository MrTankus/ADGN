
import itertools


def edges_fitness_function(network):
    return len(network.graph.edges)


def largest_connectivity_componenet_fitness_function(network):
    connectivity_components = network.graph.get_connectivity_components()
    # return max(map(lambda cc: len(cc), connectivity_components)) + len(network.graph.edges)
    return float(1 / len(connectivity_components)) + len(network.graph.edges)


def sum_square_connectivity_componenet_fitness_function(network):
    connectivity_components = network.graph.get_connectivity_components()
    return sum([len(cc) ** 2 for cc in connectivity_components])


# TODO - generate the following fitness functions

def avg_on_paths_length_fitness_function(network):
    # TODO - Bug here? final calc fitness after relays are places hangs.
    sensors = filter(lambda node: not node.get('is_relay'), network.graph.nodes.values())
    sensors_pairs = itertools.combinations(sensors, 2)
    paths = list(filter(bool, [network.graph.dijkstra(n1, n2) for (n1, n2) in sensors_pairs]))
    path_distances = list(map(len, paths))
    sum_path_distances = sum(path_distances)
    if len(path_distances):
        return sum_path_distances / len(path_distances)
    return 0


def harmonic_avg_on_paths_length_fitness_function(network):
    sensors = filter(lambda node: not node.get('is_relay'), network.graph.nodes.values())
    sensors_pairs = itertools.combinations(sensors, 2)
    paths = list(filter(bool, [network.graph.dijkstra(n1, n2) for (n1, n2) in sensors_pairs]))
    path_distances = list(map(lambda l: 1/l, map(len, paths)))
    sum_path_distances = sum(path_distances)
    if sum_path_distances:
        return len(path_distances) / sum_path_distances
    return 0


def robustness_fitness_function(network):
    pass


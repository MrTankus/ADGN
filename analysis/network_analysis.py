import random


def check_resilience(network):
    statistics = list()
    removed_nodes = 0
    while len(network.graph.nodes) > 0:
        statistics.append((removed_nodes, max(map(lambda cc: len(cc), network.graph.get_connectivity_components()))))
        random_node = random.choice(list(network.graph.nodes.values()))
        network.graph.remove_node(random_node)
        removed_nodes += 1
    return statistics

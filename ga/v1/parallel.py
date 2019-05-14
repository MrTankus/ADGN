import random

from network.v1.network import AdHocSensorNetwork


def breed_networks(n1, n2, interest_areas):
    n1_nodes = list(n1.graph.nodes.values())
    n2_nodes = list(n2.graph.nodes.values())

    n1_partial_data = set(random.choices(n1_nodes, k=random.randint(0, int(len(n1_nodes) / 2))))
    n2_compliment_data = set(node for node in filter(lambda n: n not in n1_partial_data, n2_nodes))
    n2_partial_data = set(random.choices(n2_nodes, k=random.randint(0, int(len(n2_nodes) / 2))))
    n1_compliment_data = set(node for node in filter(lambda n: n not in n2_partial_data, n1_nodes))

    offspring1 = AdHocSensorNetwork(interest_areas=interest_areas,
                                    nodes=set(map(lambda n: n.clone(), n1_partial_data.union(n2_compliment_data))))
    offspring2 = AdHocSensorNetwork(interest_areas=interest_areas,
                                    nodes=set(map(lambda n: n.clone(), n2_partial_data.union(n1_compliment_data))))
    return offspring1, offspring2


def calc_fitness(agent_id, network, fitness_func):
    return agent_id, fitness_func(network=network)

import random

from network.v2.network import ADGN


def breed_networks(n1, n2, interest_areas):
    n1_nodes = list(n1.graph.vertices)
    n2_nodes = list(n2.graph.vertices)

    n1_partial_data = set(random.choices(n1_nodes, k=random.randint(0, int(len(n1_nodes) / 2))))
    n2_compliment_data = set(node for node in filter(lambda n: n not in n1_partial_data, n2_nodes))
    n2_partial_data = set(random.choices(n2_nodes, k=random.randint(0, int(len(n2_nodes) / 2))))
    n1_compliment_data = set(node for node in filter(lambda n: n not in n2_partial_data, n1_nodes))

    offspring1 = ADGN(interest_areas=interest_areas,
                      sensors=set(map(lambda n: n.clone(), n1_partial_data.union(n2_compliment_data))))
    offspring2 = ADGN(interest_areas=interest_areas,
                      sensors=set(map(lambda n: n.clone(), n2_partial_data.union(n1_compliment_data))))
    return offspring1, offspring2

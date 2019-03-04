from network import AdHocSensorNetwork


def generate_initial_population(interest_areas, initial_population_size=10):
    networks = set()
    for i in range(initial_population_size):
        networks.add(AdHocSensorNetwork(interest_areas=interest_areas))

    for network in networks:
        network.randomize()

    return networks


def fitness(network):
    # Because of the current constraint of 1 sensor in an interest area
    # The best network will be the network with the most edges
    return len(network.edges)


def mutate(network):
    connectivity_components = network.graph.get_connectivity_components()
    smallest_component = min(connectivity_components.items(), key=lambda item: len(item[1]))
    larget_component = max(connectivity_components.items(), key=lambda item: len(item[1]))
    for node in smallest_component[1]:
        network.move_sensor(node.node_id)


def breed(n1, n2):
    pass


def evolve(networks, generations):
    best = None
    for gen in range(generations):
        for network in networks:
            best = network
            if not network.graph.is_connected():
                mutate(network)
            pass
    return best

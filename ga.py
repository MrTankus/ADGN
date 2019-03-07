import copy
import random
from network import AdHocSensorNetwork


class Agent(object):

    def __init__(self, network):
        self.network = network
        self.fitness = 0
        self.calc_fitness()

    def calc_fitness(self):
        is_connected = self.network.graph.is_connected()
        if is_connected:
            self.fitness = 10 * len(self.network.graph.edges)
        else:
            self.fitness = len(self.network.graph.edges)

    def __lt__(self, other):
        return self.fitness > other.fitness


class GA(object):

    def __init__(self, interest_areas, initial_population_size, generations, mutation_factor=0.2, death_factor=0.2):
        self.interest_areas = interest_areas
        self.initial_population_size = initial_population_size
        self.agents = self.generate_initial_population()
        self.generations = generations
        self.mutation_factor = mutation_factor
        self.death_factor = death_factor

    def generate_initial_population(self):
        agents = list()
        for i in range(self.initial_population_size):
            network = AdHocSensorNetwork(interest_areas=self.interest_areas)
            network.randomize()
            agents.append(Agent(network=network))
        return agents

    def evolve(self):
        for gen in range(self.generations):
            print("Generation: " + str(gen))
            self.calc_fitness()
            self.selection()
            self.breed()
            self.mutate()
        self.calc_fitness()
        return True

    def calc_fitness(self):
        for agent in self.agents:
            agent.calc_fitness()

    def selection(self):
        if len(self.agents) == 1:
            return
        selected_agents = sorted(self.agents, key=lambda agent: agent.fitness, reverse=True)
        self.agents = selected_agents[:int((1 - self.death_factor) * len(selected_agents))]

    def breed(self):
        all_agents = set(self.agents)
        offsprings = set()
        while len(all_agents) > 1:
            a1 = random.sample(all_agents, 1)[0]
            a2 = random.sample(all_agents, 1)[0]
            all_agents.remove(a1)
            if a2 not in all_agents:
                # we sampled the same agent
                all_agents.add(a1)
                continue
            all_agents.remove(a2)

            all_a1_nodes = list(a1.network.graph.nodes.values())
            all_a2_nodes = list(a2.network.graph.nodes.values())

            a1_nodes = set(random.choices(all_a1_nodes, k=random.randint(0, len(all_a1_nodes))))
            compliment_in_a2 = set(node for node in filter(lambda n: n not in a1_nodes, all_a2_nodes))
            a2_nodes = set(random.choices(all_a2_nodes, k=random.randint(0, len(all_a2_nodes))))
            compliment_in_a1 = set(node for node in filter(lambda n: n not in a2_nodes, all_a1_nodes))

            first_born_nodes = set(map(lambda n: copy.deepcopy(n), a1_nodes.union(compliment_in_a2)))
            first_born = AdHocSensorNetwork(interest_areas=self.interest_areas, nodes=first_born_nodes)

            second_born_nodes = set(map(lambda n: copy.deepcopy(n), a2_nodes.union(compliment_in_a1)))
            second_born = AdHocSensorNetwork(interest_areas=self.interest_areas, nodes=second_born_nodes)
            offsprings.add(Agent(network=first_born))
            offsprings.add(Agent(network=second_born))
        self.agents.extend(offsprings)

    def mutate(self):
        for agent in self.agents:
            # if random.random() >= self.mutation_factor:
            #     return
            network = agent.network
            connectivity_components = network.graph.get_connectivity_components()
            smallest_component = None
            largest_component = None
            for component_id in connectivity_components:
                connectivity_component = connectivity_components[component_id]
                smallest_component = connectivity_component if smallest_component is None or len(smallest_component) > len(
                    connectivity_component) else smallest_component
                largest_component = connectivity_component if largest_component is None or len(largest_component) <= len(
                    connectivity_component) else largest_component

            # TODO - check the distance (d) between connectivity components.
            #        if d <= 1 - try to join components
            #        if d > 1 - never mind
            for node in smallest_component:
                network.move_sensor(node.node_id)

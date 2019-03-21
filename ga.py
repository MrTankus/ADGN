import datetime
import itertools
import random

import matplotlib

from geometry.shapes import Circle

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from collections import defaultdict
from network import AdHocSensorNetwork


class Agent(object):

    def __init__(self, network, fitness_function):
        self.network = network
        self.fitness_function = fitness_function
        self.fitness = 0
        self.calc_fitness()

    def calc_fitness(self):
        self.fitness = self.fitness_function(network=self.network)

    def __lt__(self, other):
        return self.fitness > other.fitness


class GAStatistics(object):

    GEN_FITNESS = 'Gen-Fitness'
    GEN_TIME = 'Gen-Time'

    def __init__(self, ga):
        self.ga = ga
        self.statistics = defaultdict(list)

    def gen_snapshot(self, gen, time_spent):
        self.statistics[GAStatistics.GEN_FITNESS].append((gen, self.ga.get_fittest().fitness))
        self.statistics[GAStatistics.GEN_TIME].append((gen, time_spent))

    def plot_statistic(self, name):
        statistic = self.statistics.get(name)
        if statistic:
            plt.figure(name)
            ax = plt.gca()
            xs = list(map(lambda p: p[0], statistic))
            ys = list(map(lambda p: p[1], statistic))
            ax.scatter(xs, ys, s=5, c='red', alpha=1)
            ax.set_title(name)
            plt.show()
        else:
            print("No statistic with name {} was found".format(name))


class GA(object):

    def __init__(self, interest_areas, initial_population_size, generations, fitness_function, mutation_factor=0.8):
        self.interest_areas = interest_areas
        self.initial_population_size = initial_population_size
        self.fitness_function = fitness_function
        self.agents = None
        self.generations = generations
        self.mutation_factor = mutation_factor
        self.statistics = GAStatistics(ga=self)
        self.fittest_agent = None

    def generate_initial_population(self):
        initial_agents = list()
        for i in range(self.initial_population_size):
            network = AdHocSensorNetwork(interest_areas=self.interest_areas)
            network.randomize()
            initial_agents.append(Agent(network=network, fitness_function=self.fitness_function))
        self.agents = initial_agents

    def evolve(self):
        for gen in range(self.generations):
            start = datetime.datetime.now()
            print("Generation: " + str(gen))
            self.calc_fitness()
            self.selection()
            self.breed()
            self.mutate()
            self.statistics.gen_snapshot(gen=gen, time_spent=(datetime.datetime.now() - start).total_seconds())
        self.calc_fitness()
        # TODO - fix intersecting circles!
        print('Adding relays')
        self.add_relays()
        self.calc_fitness()

    def calc_fitness(self):
        for agent in self.agents:
            agent.calc_fitness()
            self.fittest_agent = agent if self.fittest_agent is None or self.fittest_agent.fitness < agent.fitness else self.fittest_agent

    def selection(self):
        selected_agents = sorted(self.agents, key=lambda agent: agent.fitness, reverse=True)
        self.agents = selected_agents[:self.initial_population_size]

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

            a1_nodes = set(random.choices(all_a1_nodes, k=random.randint(0, int(len(all_a1_nodes) / 2))))
            compliment_in_a2 = set(node for node in filter(lambda n: n not in a1_nodes, all_a2_nodes))
            a2_nodes = set(random.choices(all_a2_nodes, k=random.randint(0, int(len(all_a2_nodes) / 2))))
            compliment_in_a1 = set(node for node in filter(lambda n: n not in a2_nodes, all_a1_nodes))

            first_born_nodes = set(map(lambda n: n.clone(), a1_nodes.union(compliment_in_a2)))
            first_born = AdHocSensorNetwork(interest_areas=self.interest_areas, nodes=first_born_nodes)

            second_born_nodes = set(map(lambda n: n.clone(), a2_nodes.union(compliment_in_a1)))
            second_born = AdHocSensorNetwork(interest_areas=self.interest_areas, nodes=second_born_nodes)
            offsprings.add(Agent(network=first_born, fitness_function=self.fitness_function))
            offsprings.add(Agent(network=second_born, fitness_function=self.fitness_function))
        self.agents.extend(offsprings)

    def mutate(self):
        for agent in self.agents:
            if self.mutation_factor < random.random():
                return
            network = agent.network
            random_node = network.get_random_sensor(include_relays=False)
            network.move_sensor(random_node.node_id)

    def add_relays(self):
        for agent in self.agents:
            network = agent.network
            connectivity_components = network.graph.get_connectivity_components()
            connectivity_component_pairs = set(itertools.combinations(connectivity_components, 2))
            intersecting_connectivity_components = set(filter(lambda pair: network.get_connectivity_components_halos_intersections(cc1=pair[0], cc2=pair[1]), connectivity_component_pairs))
            visited_components = set()
            if intersecting_connectivity_components:
                for cc1, cc2 in intersecting_connectivity_components:
                    halo_intersecting_circles = network.get_connectivity_components_halos_intersections(cc1=cc1, cc2=cc2)
                    intersecting_circles = random.choice(list(halo_intersecting_circles))
                    _, relay_location = Circle.get_point_in_intersection(intersecting_circles)
                    network.add_relay(location=relay_location)
                    visited_components.add(cc1)
                    visited_components.add(cc2)
            # isolated_ccs = connectivity_components - visited_components
            # for cc in isolated_ccs:
            #     closest_node_info = network.graph.find_closest_node_to_connectivity_component(connectivity_component=cc)
            #     node_in_cc = closest_node_info[0][0]
            #     node_in_other_cc = closest_node_info[0][1]
            #     other_cc = closest_node_info[1]

    def get_fittest(self):
        if self.fittest_agent:
            return self.fittest_agent

        self.calc_fitness()
        return self.fittest_agent

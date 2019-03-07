import datetime
import copy
import random

import matplotlib
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
        self.statistics[GAStatistics.GEN_FITNESS].append((gen, max([agent.fitness for agent in self.ga.agents])))
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

    def __init__(self, interest_areas, initial_population_size, generations, fitness_function, mutation_factor=0.2):
        self.interest_areas = interest_areas
        self.initial_population_size = initial_population_size
        self.fitness_function = fitness_function
        self.agents = self.generate_initial_population(fitness_function=self.fitness_function)
        self.generations = generations
        self.mutation_factor = mutation_factor
        self.statistics = GAStatistics(ga=self)

    def generate_initial_population(self, fitness_function):
        agents = list()
        for i in range(self.initial_population_size):
            network = AdHocSensorNetwork(interest_areas=self.interest_areas)
            network.randomize()
            agents.append(Agent(network=network, fitness_function=fitness_function))
        return agents

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

    def calc_fitness(self):
        for agent in self.agents:
            agent.calc_fitness()

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

            first_born_nodes = set(map(lambda n: copy.deepcopy(n), a1_nodes.union(compliment_in_a2)))
            first_born = AdHocSensorNetwork(interest_areas=self.interest_areas, nodes=first_born_nodes)

            second_born_nodes = set(map(lambda n: copy.deepcopy(n), a2_nodes.union(compliment_in_a1)))
            second_born = AdHocSensorNetwork(interest_areas=self.interest_areas, nodes=second_born_nodes)
            offsprings.add(Agent(network=first_born, fitness_function=self.fitness_function))
            offsprings.add(Agent(network=second_born, fitness_function=self.fitness_function))
        self.agents.extend(offsprings)

    def mutate(self):
        for agent in self.agents:
            if random.random() >= self.mutation_factor:
                return
            network = agent.network
            random_node = random.choice(network.graph.nodes)
            network.move_sensor(random_node.node_id)

            # connectivity_components = network.graph.get_connectivity_components()
            # smallest_component = None
            # largest_component = None
            # for component_id in connectivity_components:
            #     connectivity_component = connectivity_components[component_id]
            #     smallest_component = connectivity_component if smallest_component is None or len(smallest_component) > len(
            #         connectivity_component) else smallest_component
            #     largest_component = connectivity_component if largest_component is None or len(largest_component) <= len(
            #         connectivity_component) else largest_component
            #
            # # TODO - check the distance (d) between connectivity components.
            # #        if d <= 1 - try to join components
            # #        if d > 1 - never mind
            # for node in smallest_component:
            #     network.move_sensor(node.node_id)

    def get_fittest(self):
        sorted_agents = sorted(self.agents, key=lambda agent: agent.fitness, reverse=True)
        return sorted_agents[0]

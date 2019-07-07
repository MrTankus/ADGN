import datetime
import hashlib
import math
import itertools
import os
import uuid
import random

from analysis.v2.fitness_functions import Optimum
from ga.v2.statistics import GAStatistics
from geometry.shapes import Circle
from network.v2.network import ADGN
from utils.v2.utils import timer


class Agent(object):

    def __init__(self, network):
        self.agent_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
        self.network = network
        self.fitness = 0

    def __lt__(self, other):
        return self.fitness > other.fitness


class GA(object):

    def __init__(self, interest_areas, initial_population_size, generations, fitness_function, mutation_factor=0.8,
                 run_id=None, network_image_saver=None, optimum=Optimum.MAX):
        self.interest_areas = interest_areas
        self.initial_population_size = initial_population_size
        self.fitness_function = fitness_function
        self.agents = None
        self.agent_mapping = dict()
        self.generations = generations
        self.mutation_factor = mutation_factor
        self.statistics = GAStatistics(ga=self)
        self.fittest_agent = None
        self.initial_fittest = None
        self.run_id = run_id
        self.network_image_saver = network_image_saver
        self.gif_images = []
        try:
            dir_name = os.path.join(os.getcwd(), 'simulations')
            os.makedirs('{}/{}/snapshots/'.format(dir_name, run_id))
        except:
            pass
        self.gen_image_path_format = 'simulations/{}/snapshots/{}.png'

        self.ga_steps = [
            ("calc fitness", self.calc_fitness),
            ("selection", self.selection),
            ("breed", self.breed),
            ("mutate", self.mutate),
        ]
        self.optimum = optimum

    def generate_initial_population(self):
        initial_agents = list()
        for i in range(self.initial_population_size):
            network = ADGN(interest_areas=self.interest_areas)
            network.randomize()
            agent = Agent(network=network)
            agent.fitness = self.fitness_function(network=agent.network)
            initial_agents.append(agent)
            self.agent_mapping[agent.agent_id] = agent
        self.agents = initial_agents

    def evolve(self):
        self.initial_fittest = self.get_fittest()
        # Synchronous evolution
        for gen in range(self.generations):
            if self.network_image_saver:
                image = self.gen_image_path_format.format(self.run_id, gen)
                self.network_image_saver(network=self.get_fittest().network, title='Gen {}'.format(gen),
                                         path=image)
                self.gif_images.append(image)
            start_ga = datetime.datetime.now()
            print("Generation: " + str(gen))
            with timer("Generation {}".format(str(gen))):
                for phase in self.ga_steps:
                    with timer(phase[0]):
                        phase[1]()
            gen_time = (datetime.datetime.now() - start_ga).total_seconds()
            self.statistics.gen_snapshot(gen=gen, time_spent=gen_time)
        print('Adding relays')
        self.add_relays()
        print('Recalculating fitness')
        self.calc_fitness()
        if self.network_image_saver:
            image = self.gen_image_path_format.format(self.run_id, self.generations)
            self.network_image_saver(network=self.get_fittest().network, title='Gen {}'.format(self.generations),
                                     path=image)
            self.gif_images.append(image)
        print("Finished GA")

    def calc_fitness(self, *args, **kwargs):
        for agent in self.agents:
            agent.fitness = self.fitness_function(network=agent.network)
            self.fittest_agent = agent if self.fittest_agent is None or self.fittest_agent.fitness < agent.fitness else self.fittest_agent

    def selection(self, *args, **kwargs):
        selected_agents = sorted(self.agents, key=lambda agent: agent.fitness, reverse=self.optimum == Optimum.MAX)
        self.agents = selected_agents[:self.initial_population_size]

    def breed(self, *args, **kwargs):
        all_agents = set(self.agents)
        offsprings = set()
        while len(all_agents) > 1:
            couple = random.sample(all_agents, 2)
            while len(couple) < 2:
                couple = random.sample(all_agents, 2)
            a1 = couple[0]
            a2 = couple[1]
            all_agents.remove(a1)
            all_agents.remove(a2)

            all_a1_nodes = list(a1.network.graph.vertices)
            all_a2_nodes = list(a2.network.graph.vertices)

            a1_nodes = set(random.choices(all_a1_nodes, k=random.randint(0, int(len(all_a1_nodes) / 2))))
            compliment_in_a2 = set(node for node in filter(lambda n: n not in a1_nodes, all_a2_nodes))
            a2_nodes = set(random.choices(all_a2_nodes, k=random.randint(0, int(len(all_a2_nodes) / 2))))
            compliment_in_a1 = set(node for node in filter(lambda n: n not in a2_nodes, all_a1_nodes))

            first_born_nodes = set(map(lambda n: n.clone(), a1_nodes.union(compliment_in_a2)))
            first_born = ADGN(interest_areas=self.interest_areas, sensors=first_born_nodes)

            second_born_nodes = set(map(lambda n: n.clone(), a2_nodes.union(compliment_in_a1)))
            second_born = ADGN(interest_areas=self.interest_areas, sensors=second_born_nodes)
            offsprings.add(Agent(network=first_born))
            offsprings.add(Agent(network=second_born))
        self.agents.extend(offsprings)

    def mutate(self, *args, **kwargs):
        for agent in self.agents:
            network = agent.network
            random_node = network.get_random_sensor(include_relays=False)
            network.move_sensor(random_node)

    def add_relays(self):
        for agent in self.agents:
            network = agent.network
            connectivity_components = set(network.graph.get_connectivity_components())
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

    def get_fittest(self):
        fittest = None
        for agent in self.agents:
            if fittest is None:
                fittest = agent
            elif self.optimum == Optimum.MAX and fittest.fitness < agent.fitness:
                fittest = agent
            elif not self.optimum == Optimum.MIN and fittest.fitness > agent.fitness > 0:
                fittest = agent
        return fittest


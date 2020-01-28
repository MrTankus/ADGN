import datetime
import hashlib
import imageio
import json
import uuid
import random

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

    def as_json_dict(self, *args, **kwargs):
        return {
            'agent_id': self.agent_id,
            'fitness': self.fitness,
            'network': self.network.as_json_dict()
        }

    @classmethod
    def from_json(cls, agent_json):
        agent_dict = json.loads(agent_json)
        return agent_dict['agent_id'], ADGN.from_json(agent_dict['network'])


class GA(object):

    def __init__(self, interest_areas, initial_population_size, generations, fitness_function, optimum, mutation_factor=0.8,
                 run_id=None):
        self.interest_areas = interest_areas
        self.initial_population_size = initial_population_size
        self.fitness_function = fitness_function
        self.agents = None
        self.generations = generations
        self.mutation_factor = mutation_factor
        self.statistics = GAStatistics(ga=self)
        self.fittest_agent = None
        self.initial_fittest = None
        self.run_id = run_id
        self.networks_for_visualization = []

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
            _, agent.fitness = self.fitness_function(agent=agent)
            initial_agents.append(agent)
        self.agents = initial_agents

    def evolve(self, logger):
        self.initial_fittest = self.get_fittest()
        self.networks_for_visualization = []
        gen_image_path_format = '{}/snapshots/{}.png'
        image = gen_image_path_format.format(self.run_id, 'initial')
        self.networks_for_visualization.append((self.initial_fittest.network.as_json_dict(), 'Gen {}'.format('initial'), image))

        for gen in range(1, self.generations):
            start_ga = datetime.datetime.now()
            logger.info("Generation: " + str(gen))
            with timer("Generation {}".format(str(gen)), logger=logger):
                for phase in self.ga_steps:
                    with timer(phase[0], logger=logger):
                        phase[1]()
            gen_time = (datetime.datetime.now() - start_ga).total_seconds()
            self.statistics.gen_snapshot(gen=gen, time_spent=gen_time)
            image = gen_image_path_format.format(self.run_id, gen)
            network_visualization_info = (self.get_fittest().network.as_json_dict(), 'Gen {}'.format(gen), image)
            self.networks_for_visualization.append(network_visualization_info)

        logger.info('Adding relays')
        self.add_relays()
        logger.info('Recalculating fitness')
        self.calc_fitness()
        image = gen_image_path_format.format(self.run_id, self.generations)
        network_visualization_info = (self.get_fittest().network.as_json_dict(), 'Gen {}'.format(self.generations), image)
        self.networks_for_visualization.append(network_visualization_info)
        logger.info("Finished GA")

    def calc_fitness(self, *args, **kwargs):
        for agent in self.agents:
            _, agent.fitness = self.fitness_function(agent=agent)
            self.fittest_agent = agent if self.fittest_agent is None or self.fittest_agent.fitness < agent.fitness else self.fittest_agent

    def selection(self, *args, **kwargs):
        from analysis.v2.fitness_functions import Optimum
        selected_agents = sorted(self.agents, key=lambda agent: agent.fitness, reverse=self.optimum == Optimum.MAX)
        self.agents = selected_agents[:self.initial_population_size]

    def breed(self, *args, **kwargs):
        all_agents = list(self.agents)
        offsprings = set()
        while len(all_agents) > 1:

            a1 = random.choice(all_agents)
            all_agents.remove(a1)
            a2 = random.choice(all_agents)
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
            if random.random() <= self.mutation_factor:
                random_node = network.get_random_sensor(include_relays=False)
                network.move_sensor(random_node)

    def add_relays(self):
        relevant_agents = set(filter(lambda t: len(t[1]) > 0, map(lambda agent: (agent, agent.network.get_intersecting_connectivity_components()), self.agents)))
        while len(relevant_agents) > 0:
            agent, ccs = relevant_agents.pop()
            ccs = set(ccs)
            network = agent.network
            cc1, cc2 = ccs.pop()
            halo_intersecting_circles = network.get_connectivity_components_halos_intersections(cc1=cc1, cc2=cc2)
            intersecting_circles = random.choice(list(halo_intersecting_circles))
            _, relay_location = Circle.get_point_in_intersection(intersecting_circles)
            network.add_relay(location=relay_location)
            new_intersecting_connectivity_components = network.get_intersecting_connectivity_components()
            if new_intersecting_connectivity_components:
                relevant_agents.add((agent, new_intersecting_connectivity_components))

    def get_fittest(self):
        from analysis.v2.fitness_functions import Optimum
        fittest = None
        for agent in self.agents:
            if fittest is None:
                fittest = agent
            elif self.optimum == Optimum.MAX and fittest.fitness < agent.fitness:
                fittest = agent
            elif not self.optimum == Optimum.MIN and fittest.fitness > agent.fitness > 0:
                fittest = agent
        return fittest

    def generate_evolution_visualization(self, network_image_saver, output_dir):
        if network_image_saver:
            images_for_visualization = []
            for network_visualization_info in self.networks_for_visualization:
                network = ADGN.from_json(network_visualization_info[0])
                title = network_visualization_info[1]
                image_path = '{}/{}'.format(output_dir, network_visualization_info[2])
                network_image_saver(network, title, image_path)
                images_for_visualization.append(imageio.imread(image_path))
            imageio.mimsave('{}/{}/network_evolution.gif'.format(output_dir, self.run_id), images_for_visualization,
                            duration=0.2)


class ParallelGA(GA):

    def __init__(self, interest_areas, initial_population_size, generations, fitness_function, optimum, pool, mutation_factor=0.8,
                 run_id=None):

        super(ParallelGA, self).__init__(interest_areas=interest_areas, initial_population_size=initial_population_size,
                                         generations=generations, fitness_function=fitness_function, optimum=optimum,
                                         mutation_factor=mutation_factor, run_id=run_id)
        self.pool = pool
        from ga.v2.parallel import breed_networks
        self.parallel_breed = breed_networks
        self.agent_mapping = dict()

    def generate_initial_population(self):
        super(ParallelGA, self).generate_initial_population()
        self.agent_mapping = dict(map(lambda agent: (agent.agent_id, agent), self.agents))

    def selection(self, *args, **kwargs):
        super(ParallelGA, self).selection(*args, **kwargs)
        self.agent_mapping = dict(map(lambda agent: (agent.agent_id, agent), self.agents))

    def calc_fitness(self, *args, **kwargs):
        for res in self.pool.map(self.fitness_function, self.agents):
            agent = self.agent_mapping[res[0]]
            agent.fitness = res[1]
            self.fittest_agent = agent if self.fittest_agent is None or self.fittest_agent.fitness < agent.fitness else self.fittest_agent

    def breed(self, *args, **kwargs):
        all_agents = list(self.agents)
        breeding_info = list()
        while len(all_agents) > 1:
            a1 = random.choice(all_agents)
            all_agents.remove(a1)
            a2 = random.choice(all_agents)
            all_agents.remove(a2)
            breeding_info.append((a1.network, a2.network, self.interest_areas))

        offsprings = list()
        for res in self.pool.starmap(self.parallel_breed, breeding_info):
            agent1 = Agent(network=res[0])
            agent2 = Agent(network=res[1])
            self.agent_mapping[agent1.agent_id] = agent1
            self.agent_mapping[agent2.agent_id] = agent2
            offsprings.append(agent1)
            offsprings.append(agent2)
        self.agents.extend(offsprings)

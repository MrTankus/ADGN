import hashlib
import uuid
import itertools
import numpy as np
import pandas as pd

from network.network import ADGN
from utils.utils import timer


class Agent(object):

    def __init__(self, network, fitness_function):
        self.agent_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
        self.network = network
        self.fitness = fitness_function(self)[1]


class SGD(object):

    def __init__(self, run_id, interest_areas, fitness_function, optimum, iterations):
        self.run_id = run_id
        self.interest_areas = interest_areas
        self.fitness_function = fitness_function
        self.optimum = optimum
        self.iterations = iterations
        self.phases = {
            'create_adversarial_network': self.create_adversarial_network,
            'change_network': self.change_network
        }
        self.agent = Agent(network=ADGN(interest_areas=self.interest_areas), fitness_function=fitness_function)
        self.agent.network.randomize()
        self.statistics = None

    def get_fittest(self):
        return self.agent

    def generate_evolution_visualization(self, *args, **kwargs):
        pass

    def evolve(self, logger):
        for iteration in range(self.iterations):
            logger.info("Iteration %s", iteration)
            result = None
            for phase in self.phases:
                name = phase
                operation = self.phases[phase]
                with timer(op_name=name, logger=logger):
                    result = operation(result, logger)

    def create_adversarial_network(self, result, logger, *args, **kwargs):
        vertices = list(self.agent.network.graph.vertices)
        df = pd.DataFrame([v.get('location') for v in vertices], index=[v.id for v in vertices], columns=['x', 'y'])
        epsilon = np.random.uniform()
        df['id'] = df.index
        df['ia_radius'] = np.array([v.get('interest_area').radius for v in vertices])
        df['ia_center-x'] = np.array([v.get('interest_area').center[0] for v in vertices])
        df['ia_center-y'] = np.array([v.get('interest_area').center[1] for v in vertices])
        df['new-x'] = df['x'] + np.random.uniform(size=len(self.agent.network.graph.vertices)) * epsilon
        df['new-y'] = df['y'] + np.random.uniform(size=len(self.agent.network.graph.vertices)) * epsilon

        def apply(data):
            from network.interest_areas import InterestArea
            ia = InterestArea(center=(data['ia_center-x'], data['ia_center-y']), radius=data['ia_radius'], name='dummy')
            return ia.is_in_circle((data['new-x'], data['new-y']))

        # df[df.apply(apply, axis=1)]
        pass

    def change_network(self, adversary_network, logger, *args, **kwargs):
        adversary_agent = Agent(network=adversary_network, fitness_function=self.fitness_function)

        if adversary_agent.fitness > self.agent.fitness:
            self.agent = adversary_agent
        else:
            probability = np.exp(1 * (adversary_agent.fitness - self.agent.fitness))
            if np.random.uniform() < probability:
                self.agent = adversary_agent

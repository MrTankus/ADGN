import hashlib
import itertools
import math
import uuid
import random

from geometry.shapes import Circle
from graphs.graphs import Vertex, DiskGraph
from network.interest_areas import InterestArea


class ADGN(object):

    def __init__(self, interest_areas, sensors=None):
        self.interest_areas = set(interest_areas)
        self.graph = DiskGraph(vertices=sensors, radius=1)
        self.relays = set()

    def as_json_dict(self, *args, **kwargs):
        res = {
            'interest_areas': [ia.as_json_dict() for ia in self.interest_areas],
            'graph': self.graph.as_json_dict(with_edges=True),
        }
        return res

    @classmethod
    def from_json(cls, network_json):
        interest_areas = {InterestArea.from_json(ia_json) for ia_json in network_json['interest_areas']}
        graph = DiskGraph.from_json(network_json['graph'])
        adgn = ADGN(interest_areas=interest_areas, sensors=graph.vertices)
        adgn.relays = set(filter(lambda v: v.get('is_relay'), graph.vertices))
        return adgn

    @staticmethod
    def generate_random_sensor_location(interest_area, mid_center=False):
        if mid_center:
            return interest_area.center[0], interest_area.center[1]
        argument = 2 * math.pi * random.random()
        r = interest_area.radius * random.random()
        x_location = interest_area.center[0] + r * math.cos(argument)
        y_location = interest_area.center[1] + r * math.sin(argument)
        return x_location, y_location

    @classmethod
    def is_valid_location(cls, vertex, location):
        ia = vertex.get('interest_area')
        if ia:
            return ia.is_in_circle(location)
        return True

    def randomize(self):
        sensor_id = 0
        for interest_area in self.interest_areas:
            data = {
                'interest_area': interest_area,
                'is_relay': False
            }
            sensor = self.create_sensor(vertex_id=sensor_id,
                                        location=self.generate_random_sensor_location(interest_area=interest_area,
                                                                                      mid_center=interest_area.is_hub),
                                        **data)
            self.graph.add_vertex(sensor)
            sensor_id += 1

    @staticmethod
    def create_sensor(vertex_id, location, *args, **kwars):
        return Vertex(vertex_id, location=location, **kwars)

    def move_sensor(self, sensor):
        if sensor not in self.graph.vertices:
            return False

        self.hop_random(sensor=sensor)
        self.graph.construct_edges(vertex=sensor)

    def hop_random(self, sensor):
        '''
        Moves a sensor to a random location inside its interest_area
        Note: This miethod is not under the Sensor class for a reason!
        :param sensor: the sensor to be moved
        :return:
        '''
        sensor.set('location', self.generate_random_sensor_location(interest_area=sensor.get('interest_area')))

    def get_random_sensor(self, include_relays=True):
        if include_relays:
            return random.sample(self.graph.vertices, 1)[0]
        else:
            non_relays = set(filter(lambda sensor: not sensor.get('is_relay', False), self.graph.vertices))
            if non_relays:
                return random.sample(non_relays, 1)[0]
            return None

    @staticmethod
    def get_connectivity_components_halos_intersections(cc1, cc2):

        def get_vertex_halo(v):
            return Circle(center=v.get('location'), radius=v.get('halo'))

        cc1_halo = map(lambda sensor: get_vertex_halo(sensor), cc1)
        cc2_halo = map(lambda sensor: get_vertex_halo(sensor), cc2)
        intersecting_circles = set()
        visited_circles = set()
        for c1 in cc1_halo:
            for c2 in cc2_halo:
                pair_set = frozenset([c1, c2])
                if c1 != c2 and pair_set not in visited_circles and c1.intersects(c2):
                    visited_circles.add(pair_set)
                    intersecting_circles.add((c1, c2))
        return intersecting_circles

    def get_intersecting_connectivity_components(self):
        intersecting_connectivity_components = set(
            filter(lambda pair: self.get_connectivity_components_halos_intersections(cc1=pair[0], cc2=pair[1]),
                   itertools.combinations(self.graph.get_connectivity_components(), 2)))
        return frozenset(intersecting_connectivity_components)

    def add_relay(self, location, *args, **kwargs):
        random_vertex_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
        data = {
            'is_relay': True,
            'location': location
        }
        data.update(**kwargs)
        vertex = Vertex(random_vertex_id, **data)
        self.graph.add_vertex(vertex)
        self.relays.add(random_vertex_id)

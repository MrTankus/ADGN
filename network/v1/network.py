import json
import math
import random
import uuid
import hashlib

from graphs.v1.graphs import UDG
from graphs.v1.nodes import GeometricNode


class AdHocSensorNetwork(object):

    def __init__(self, interest_areas, nodes=None):
        self.interest_areas = set(interest_areas)
        self.graph = UDG(nodes=nodes)
        self.relays = set()

    @staticmethod
    def generate_random_sensor_location(interest_area, mid_center=False):
        if mid_center:
            return interest_area.center[0], interest_area.center[1]
        argument = 2 * math.pi * random.random()
        r = interest_area.radius * random.random()
        x_location = interest_area.center[0] + r * math.cos(argument)
        y_location = interest_area.center[1] + r * math.sin(argument)
        return x_location, y_location

    def randomize(self):
        sensor_id = 0
        for interest_area in self.interest_areas:
            data = {
                'interest_area': interest_area,
                'is_relay': False
            }
            self.graph.add_node(node_id=sensor_id, data=data,
                                location=self.generate_random_sensor_location(interest_area=interest_area,
                                                                              mid_center=interest_area.is_hub))
            sensor_id += 1

    def get_random_sensor(self, include_relays=True):
        if include_relays:
            return random.choice(self.graph.nodes)
        else:
            relays = list(filter(lambda sensor: sensor.get('is_relay'), self.graph.nodes.values()))
            if relays:
                return random.choice(relays)
            else:
                return random.choice(self.graph.nodes)

    def get_connectivity_components_halos_intersections(self, cc1, cc2):
        cc1_halo = map(lambda sensor: sensor.get_node_halo(), cc1)
        cc2_halo = map(lambda sensor: sensor.get_node_halo(), cc2)
        intersecting_circles = set()
        visited_circles = set()
        for c1 in cc1_halo:
            for c2 in cc2_halo:
                pair_set = frozenset([c1, c2])
                if c1 != c2 and pair_set not in visited_circles and c1.intersects(c2):
                    visited_circles.add(pair_set)
                    intersecting_circles.add((c1, c2))
        return intersecting_circles

    def get_other_ccs_info(self, connectivity_component):
        all_ccs = self.graph.get_connectivity_components() - connectivity_component
        res = list()
        for cc in all_ccs:
            res.extend([(n1.distance_from(n2), [n1, n2], cc, n1.get_node_halo().intersects(n2.get_node_halo())) for n1 in connectivity_component for n2 in cc])
        return sorted(res, key=lambda t: t[0])

    def move_sensor(self, sensor_id):
        if sensor_id not in self.graph.nodes:
            return False

        sensor = self.graph.nodes[sensor_id]
        self.hop_random(sensor=sensor)
        self.graph.construct_edges(node=sensor)

    def add_relay(self, location, *args, **kwargs):
        random_node_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
        data = {
            'is_relay': True
        }

        self.graph.add_node(node_id=random_node_id, data=data, location=location, *args, **kwargs)
        self.relays.add(random_node_id)

    def add_relays_between_sensors(self, n1, n2):
        distance_between_sensors = self.graph.geo_distance(n1, n2)
        number_of_sensors = int(distance_between_sensors)
        relay_location = n1.location
        for i in range(number_of_sensors):
            relay_location = (relay_location[0] + (i+1)/number_of_sensors, relay_location[1] + (i+1)/number_of_sensors)
            self.add_relay(location=relay_location)

    def hop_random(self, sensor):
        '''
        Moves a sensor to a random location inside its interest_area
        Note: This miethod is not under the Sensor class for a reason!
        :param sensor: the sensor to be moved
        :return:
        '''
        sensor.location = self.generate_random_sensor_location(interest_area=sensor.get('interest_area'))

    def validate(self):
        self.graph.validate()

    def as_json(self):
        network_data = {
            'interest_areas': [{
                'name': interest_area.name,
                'center': interest_area.center,
                'radius': interest_area.radius,
                'is_hub': interest_area.is_hub
            } for interest_area in self.interest_areas],
            'sensors': [{
                'node_id': node.node_id,
                'location': node.location,
                'halo': node.halo,
                'interest_area': node.data['interest_area'].name if not node.data['is_relay'] else None,
                'is_relay': node.data['is_relay']

            } for node in self.graph.nodes.values()]
        }
        return json.dumps(network_data)

    @classmethod
    def from_json(cls, network_json):
        interest_areas = dict()
        nodes = set()
        for ia in network_json['interest_areas']:
            interest_areas[ia['name']] = InterestArea(center=tuple(ia['center']), radius=ia['radius'], name=ia['name'],
                                                      is_hub=ia['is_hub'])
        for node in network_json['sensors']:
            node_data = {
                'is_relay': node['is_relay']
            }
            if not node['is_relay']:
                node_data['interest_area'] = interest_areas.get(node['interest_area'])
            nodes.add(GeometricNode(node_id=node['node_id'], location=node['location'], data=node_data,
                                    halo=node['halo']))
        return cls(interest_areas=interest_areas.values(), nodes=nodes)

    def export(self, to_file):
        with open(to_file, 'w') as f:
            f.write(self.as_json())

    @classmethod
    def import_network(cls, from_file):
        with open(from_file, 'r') as f:
            network_json = json.loads(f.read())
            network = cls.from_json(network_json=network_json)
        return network

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle as CircleUI
from matplotlib.lines import Line2D

import math
import random
import uuid
import hashlib
from geometry.shapes import Circle
from graphs.graphs import UDG


class InterestArea(Circle):

    def __init__(self, center, radius, name, is_hub=False):
        super(InterestArea, self).__init__(center=center, radius=radius)
        self.name = name
        self.is_hub = is_hub


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

    def get_connectivity_component_halo(self, connectivity_component):
        return map(lambda sensor: Circle(center=sensor.location, radius=sensor.halo), connectivity_component)

    def get_connectivity_components_halos_intersections(self, cc1, cc2):
        cc1_halo = self.get_connectivity_component_halo(connectivity_component=cc1)
        cc2_halo = self.get_connectivity_component_halo(connectivity_component=cc2)
        intersectin_circles = set()
        visited_circles = set()
        for c1 in cc1_halo:
            for c2 in cc2_halo:
                pair_set = frozenset([c1, c2])
                if c1 != c2 and pair_set not in visited_circles and c1.intersects(c2):
                    visited_circles.add(pair_set)
                    intersectin_circles.add((c1, c2))
        return intersectin_circles

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

    def hop_random(self, sensor):
        '''
        Moves a sensor to a random location inside its interest_area
        Note: This miethod is not under the Sensor class for a reason!
        :param sensor: the sensor to be moved
        :return:
        '''
        sensor.location = self.generate_random_sensor_location(interest_area=sensor.get('interest_area'))

    def export(self):
        network_data = {
            'interest_areas': [{
                'center': interest_area.center,
                'radius': interest_area.radius,
                'is_hub': interest_area.is_hub
            } for interest_area in self.interest_areas],
            'sensors': [{
                'node_id': node.node_id,
                'location': node.location,
                'halo': node.halo,

            } for node in self.graph.nodes.values()]
        }

    def plot(self, fig_id, title, xlims, ylims):
        plt.figure(fig_id)
        ax = plt.gca()
        for ia in self.interest_areas:
            color = 'blue' if not ia.is_hub else 'green'
            c = CircleUI((ia.center[0], ia.center[1]), ia.radius, facecolor=color, edgecolor='black')
            c.set_alpha(0.5)
            c.set_label(ia.name)
            ax.add_patch(c)
            ax.annotate(ia.name, xy=(ia.center[0], ia.center[1]), fontsize=8, ha="center")
        sensors_xs = []
        sensors_ys = []
        relays_xs = []
        relays_ys = []
        for sensor_id in self.graph.nodes:
            sensor = self.graph.nodes[sensor_id]
            if sensor.get(key='is_relay'):
                relays_xs.append(sensor.location[0])
                relays_ys.append(sensor.location[1])
            else:
                sensors_xs.append(sensor.location[0])
                sensors_ys.append(sensor.location[1])
        ax.scatter(sensors_xs, sensors_ys, s=5, c='red', alpha=1)
        ax.scatter(relays_xs, relays_ys, s=5, c='green', alpha=1)
        for edge in self.graph.edges:
            sensor1 = self.graph.nodes[edge.node1.node_id]
            sensor2 = self.graph.nodes[edge.node2.node_id]
            ui_line = Line2D([sensor1.location[0], sensor2.location[0]], [sensor1.location[1], sensor2.location[1]],
                             linewidth=1, color='black')
            ax.add_line(ui_line)

        ax.set_title('Adhoc Network')
        plt.xlim(xlims[0], xlims[1])
        plt.ylim(ylims[0], ylims[1])
        plt.title(title)
        plt.show()

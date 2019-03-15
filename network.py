import string

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle as CircleUI
from matplotlib.lines import Line2D

import math
import random
import uuid
import hashlib
from geometry import Point, Circle
from graph import GeometricNode, UDG


class InterestArea(Circle):

    def __init__(self, center, radius, name, is_hub=False):
        super(InterestArea, self).__init__(center=center, radius=radius)
        self.name = name
        self.is_hub = is_hub


class Sensor(GeometricNode):

    def __init__(self, id, interest_area, distance_from_ia_center, argument, sensing_radius):
        assert 0 <= distance_from_ia_center <= interest_area.radius
        self.id = id
        self._distance_from_ia_center = distance_from_ia_center
        self._argument = argument
        self.interest_area = interest_area
        super(Sensor, self).__init__(node_id=id, location=self.get_location(
                                     distance_from_ia_center=self._distance_from_ia_center, argument=self._argument),
                                     halo=sensing_radius)

    def get_location(self, distance_from_ia_center, argument):
        assert 0 <= distance_from_ia_center <= self.interest_area.radius
        self._distance_from_ia_center = distance_from_ia_center
        self._argument = argument
        x_location = self.interest_area.center.x + self._distance_from_ia_center * math.cos(self._argument)
        y_location = self.interest_area.center.y + self._distance_from_ia_center * math.sin(self._argument)
        return Point(x=x_location, y=y_location)

    def sensing_radius(self):
        return self.halo

    def clone(self):
        return Sensor(id=self.id, interest_area=self.interest_area,
                      distance_from_ia_center=self._distance_from_ia_center, argument=self._argument,
                      sensing_radius=self.halo)


class RelaySensor(GeometricNode):

    def __init__(self, node_id, location, sensing_radius):
        super(RelaySensor, self).__init__(node_id=node_id, location=location, halo=sensing_radius)


class AdHocSensorNetwork(object):

    def __init__(self, interest_areas, nodes=None):
        self.interest_areas = set(interest_areas)
        self.graph = UDG(nodes=nodes)
        self.interest_area_clusters = set()
        self.relays = set()

    def randomize(self):
        sensor_id = 0
        for interest_area in self.interest_areas:
            if interest_area.is_hub:
                sensor = Sensor(id=sensor_id, interest_area=interest_area, distance_from_ia_center=0, argument=0,
                                sensing_radius=1)
            else:
                argument = 2 * math.pi * random.random()
                r = interest_area.radius * random.random()
                sensor = Sensor(id=sensor_id, interest_area=interest_area, distance_from_ia_center=r, argument=argument,
                                sensing_radius=1)
            self.graph.add_node(sensor)
            sensor_id += 1
        self.graph.original_node_count = len(self.graph.nodes)

    def get_random_sensor(self, include_relays=True):
        if include_relays:
            return random.choice(self.graph.nodes.values())
        else:
            relays = list(filter(lambda sensor: isinstance(sensor, Sensor), self.graph.nodes.values()))
            if relays:
                return random.choice(relays)
            else:
                return random.choice(self.graph.nodes.values())

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
        self.graph.add_node(node=RelaySensor(node_id=random_node_id, location=location, sensing_radius=1), *args, **kwargs)
        self.relays.add(random_node_id)

    def hop_random(self, sensor):
        '''
        Moves a sensor to a random location inside its interest_area
        Note: This miethod is not under the Sensor class for a reason!
        :param sensor: the sensor to be moved
        :return:
        '''
        radius = sensor.interest_area.radius * random.random()
        argument = 2 * math.pi * random.random()
        sensor.location = sensor.get_location(distance_from_ia_center=radius, argument=argument)

    def plot(self, fig_id, title, xlims, ylims):
        plt.figure(fig_id)
        ax = plt.gca()
        for ia in self.interest_areas:
            color = 'blue' if not ia.is_hub else 'green'
            c = CircleUI((ia.center.x, ia.center.y), ia.radius, facecolor=color, edgecolor='black')
            c.set_alpha(0.5)
            c.set_label(ia.name)
            ax.add_patch(c)
            ax.annotate(ia.name, xy=(ia.center.x, ia.center.y), fontsize=8, ha="center")
        sensors_xs = []
        sensors_ys = []
        relays_xs = []
        relays_ys = []
        for sensor_id in self.graph.nodes:
            sensor = self.graph.nodes[sensor_id]
            if isinstance(sensor, RelaySensor):
                relays_xs.append(sensor.location.x)
                relays_ys.append(sensor.location.y)
            else:
                sensors_xs.append(sensor.location.x)
                sensors_ys.append(sensor.location.y)
        ax.scatter(sensors_xs, sensors_ys, s=5, c='red', alpha=1)
        ax.scatter(relays_xs, relays_ys, s=5, c='green', alpha=1)
        for edge in self.graph.edges:
            sensor1 = self.graph.nodes[edge.node1.node_id]
            sensor2 = self.graph.nodes[edge.node2.node_id]
            ui_line = Line2D([sensor1.location.x, sensor2.location.x], [sensor1.location.y, sensor2.location.y],
                             linewidth=1, color='black')
            ax.add_line(ui_line)

        ax.set_title('Adhoc Network')
        plt.xlim(xlims[0], xlims[1])
        plt.ylim(ylims[0], ylims[1])
        plt.title(title)
        plt.show()

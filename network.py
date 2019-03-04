import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle as CircleUI
from matplotlib.lines import Line2D

import math
import random
from geometry import Point, Circle
from graph import GeometricNode, UDG


class InterestArea(Circle):

    def __init__(self, center, radius, name, is_hub=False):
        super(InterestArea, self).__init__(center=center, radius=radius)
        self.name = name
        self.is_hub = is_hub


class Sensor(GeometricNode):

    def __init__(self, id, interest_area, r, argument, sensing_radius):
        assert 0 <= r <= interest_area.radius
        self.id = id
        self._r = r
        self._argument = argument
        self.interest_area = interest_area
        super(Sensor, self).__init__(node_id=id, location=self.get_location(radius=self._r, argument=self._argument),
                                     halo=sensing_radius)

    def distance_from(self, sensor):
        return self.location.distance(sensor.location)

    def hop_random(self):
        radius = self.interest_area.radius * random.random()
        argument = 2 * math.pi * random.random()
        self.location = self.get_location(radius=radius, argument=argument)

    def get_location(self, radius=None, argument=None):
        assert 0 <= radius <= self.interest_area.radius
        self._r = radius
        self._argument = argument
        x_location = self.interest_area.center.x + self._r * math.cos(self._argument)
        y_location = self.interest_area.center.y + self._r * math.sin(self._argument)
        return Point(x=x_location, y=y_location)

    def sensing_radius(self):
        return self.halo


class AdHocSensorNetwork(object):

    def __init__(self, interest_areas):
        self.interest_areas = interest_areas
        self.graph = UDG()

    def randomize(self):
        sensor_id = 0
        for interest_area in self.interest_areas:
            if interest_area.is_hub:
                sensor = Sensor(id=sensor_id, interest_area=interest_area, r=0, argument=0,
                                sensing_radius=1)
            else:
                argument = 2 * math.pi * random.random()
                r = interest_area.radius * random.random()
                sensor = Sensor(id=sensor_id, interest_area=interest_area, r=r, argument=argument,
                                sensing_radius=1)
            self.graph.add_node(sensor)
            sensor_id += 1

    def move_sensor(self, sensor_id):
        if sensor_id not in self.graph.nodes:
            return False

        sensor = self.graph.nodes[sensor_id]
        sensor.hop_random()
        self.graph.construct_edges(node=sensor)

    def plot(self, fig_id, xlims, ylims):
        plt.figure(fig_id)
        ax = plt.gca()
        for ia in self.interest_areas:
            color = 'blue' if not ia.is_hub else 'green'
            c = CircleUI((ia.center.x, ia.center.y), ia.radius, facecolor=color, edgecolor='black')
            c.set_alpha(0.5)
            c.set_label(ia)
            ax.add_artist(c)
        xs = []
        ys = []
        for sensor_id in self.graph.nodes:
            sensor = self.graph.nodes[sensor_id]
            xs.append(sensor.location.x)
            ys.append(sensor.location.y)
        ax.scatter(xs, ys, s=5, c='red', alpha=1)
        for edge in self.graph.edges:
            sensor1 = self.graph.nodes[edge.node1.node_id]
            sensor2 = self.graph.nodes[edge.node2.node_id]
            ui_line = Line2D([sensor1.location.x, sensor2.location.x], [sensor1.location.y, sensor2.location.y],
                             linewidth=1, color='black')
            ax.add_line(ui_line)

        ax.set_title('Adhoc Network')
        plt.xlim(xlims[0], xlims[1])
        plt.ylim(ylims[0], ylims[1])
        plt.show()

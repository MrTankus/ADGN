import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle as CircleUI
from matplotlib.lines import Line2D


def plot_network(network, title, xlims, ylims):
    plt.figure()
    ax = plt.gca()
    for ia in network.interest_areas:
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
    for sensor_id in network.graph.nodes:
        sensor = network.graph.nodes[sensor_id]
        if sensor.get(key='is_relay'):
            relays_xs.append(sensor.location[0])
            relays_ys.append(sensor.location[1])
        else:
            sensors_xs.append(sensor.location[0])
            sensors_ys.append(sensor.location[1])
    ax.scatter(sensors_xs, sensors_ys, s=5, c='red', alpha=1)
    ax.scatter(relays_xs, relays_ys, s=5, c='green', alpha=1)
    for edge in network.graph.edges:
        sensor1 = network.graph.nodes[edge.node1.node_id]
        sensor2 = network.graph.nodes[edge.node2.node_id]
        ui_line = Line2D([sensor1.location[0], sensor2.location[0]], [sensor1.location[1], sensor2.location[1]],
                         linewidth=1, color='black')
        ax.add_line(ui_line)

    ax.set_title('Adhoc Network')
    plt.xlim(xlims[0], xlims[1])
    plt.ylim(ylims[0], ylims[1])
    plt.title(title)
    plt.show()
    plt.show()


def plot_statistics(name, statistic, with_id_line=False):
    if statistic:
        plt.figure(name)
        ax = plt.gca()
        xs = list(map(lambda p: p[0], statistic))
        ys = list(map(lambda p: p[1], statistic))
        ax.scatter(xs, ys, s=5, c='red', alpha=1)
        if with_id_line:
            ax.scatter(xs, xs, s=5, c='black', alpha=1)
        ax.set_title(name)
        plt.show()
    else:
        print("No statistic with name {} was found".format(name))

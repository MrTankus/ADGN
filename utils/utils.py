import argparse
import datetime
from contextlib import contextmanager

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
    for sensor in network.graph.vertices:
        if sensor.get(key='is_relay'):
            relays_xs.append(sensor.get('location')[0])
            relays_ys.append(sensor.get('location')[1])
        else:
            sensors_xs.append(sensor.get('location')[0])
            sensors_ys.append(sensor.get('location')[1])
    ax.scatter(sensors_xs, sensors_ys, s=5, c='red', alpha=1)
    ax.scatter(relays_xs, relays_ys, s=5, c='green', alpha=1)
    for edge in network.graph.edges:
        sensor1 = edge.v1
        sensor2 = edge.v2
        ui_line = Line2D([sensor1.get('location')[0], sensor2.get('location')[0]], [sensor1.get('location')[1], sensor2.get('location')[1]],
                         linewidth=1, color='black')
        ax.add_line(ui_line)

    ax.set_title('Adhoc Network')
    plt.xlim(xlims[0], xlims[1])
    plt.ylim(ylims[0], ylims[1])
    plt.title(title)
    plt.show()


def save_network_image(network, title, path):
    fig = plt.figure()
    ax = fig.gca()
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
    for sensor in network.graph.vertices:
        if sensor.get(key='is_relay'):
            relays_xs.append(sensor.get('location')[0])
            relays_ys.append(sensor.get('location')[1])
        else:
            sensors_xs.append(sensor.get('location')[0])
            sensors_ys.append(sensor.get('location')[1])
    ax.scatter(sensors_xs, sensors_ys, s=5, c='red', alpha=1)
    ax.scatter(relays_xs, relays_ys, s=5, c='green', alpha=1)
    for edge in network.graph.edges:
        sensor1 = edge.v1
        sensor2 = edge.v2
        ui_line = Line2D([sensor1.get('location')[0], sensor2.get('location')[0]],
                         [sensor1.get('location')[1], sensor2.get('location')[1]],
                         linewidth=1, color='black')
        ax.add_line(ui_line)

    ax.set_title(title)
    fig.savefig(path)
    plt.close(fig)
    plt.close('all')


def save_statistics(name, statistic, path, generate_ys=None):
    if statistic:
        fig = plt.figure(name)
        ax = plt.gca()
        xs = list(map(lambda p: p[0], statistic))
        ys = list(map(lambda p: p[1], statistic))
        ax.scatter(xs, ys, s=5, c='red', alpha=1)
        if generate_ys:
            ax.scatter(xs, generate_ys(xs), s=5, c='black', alpha=1)
        ax.set_title(name)
        fig.savefig(path)
        plt.close(fig)
        plt.close('all')
    else:
        print("No statistic with name {} was found".format(name))


def plot_interest_areas(interest_areas, xlims, ylims):
    plt.figure()
    ax = plt.gca()
    for ia in interest_areas:
        color = 'blue' if not ia.is_hub else 'green'
        c = CircleUI((ia.center[0], ia.center[1]), ia.radius, facecolor=color, edgecolor='black')
        c.set_alpha(0.5)
        c.set_label(ia.name)
        ax.add_patch(c)
        ax.annotate(ia.name, xy=(ia.center[0], ia.center[1]), fontsize=8, ha="center")

    plt.xlim(xlims[0], xlims[1])
    plt.ylim(ylims[0], ylims[1])
    plt.title('Interest Areas')
    plt.show()


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

@contextmanager
def timer(op_name, logger=None):
    start = datetime.datetime.now()
    try:
        yield
    finally:
        end = datetime.datetime.now()
        message = "Operation: {} took {} seconds".format(op_name, (end - start).total_seconds())
        if logger:
            logger.info(message)
        else:
            print(message)

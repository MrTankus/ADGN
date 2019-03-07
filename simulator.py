import random
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle as CircleUI
from network import InterestArea
from geometry import Point
from ga import GA, GAStatistics

# interest_areas = [
#     InterestArea(center=Point(0, 0), radius=0.5, name='HUB', is_hub=True),
#     InterestArea(center=Point(1, 0.5), radius=0.5, name='Omega1'),
#     InterestArea(center=Point(2, 0), radius=0.5, name='Omeg2'),
#     InterestArea(center=Point(1, -0.5), radius=0.5, name='Omega3'),
# ]

X_LIMS = (-7, 7)
Y_LIMS = (-7, 7)
NUMBER_OF_INTEREST_AREAS = 100
RUN_GA = True


def generate_interest_areas():
    interest_areas = set()
    interest_area_id = 1
    while len(interest_areas) < NUMBER_OF_INTEREST_AREAS:
        ia = InterestArea(center=Point(x=(X_LIMS[0] + 1) + (X_LIMS[1] - 1 - X_LIMS[0] - 1) * random.random(),
                                       y=(Y_LIMS[0] + 1) + (Y_LIMS[1] - 1 - Y_LIMS[0] - 1) * random.random()),
                          radius=0.5, name='Omega' + str(interest_area_id))
        if not any(other.intersects(ia) for other in interest_areas):
            interest_areas.add(ia)

    hub = random.sample(interest_areas, 1)[0]
    hub.name = 'HUB'
    hub.is_hub = True

    return interest_areas


def edges_fitness_function(network):
    is_connected = network.graph.is_connected()
    if is_connected:
        return 10 * len(network.graph.edges)
    else:
        return len(network.graph.edges)


def largest_connectivity_componenet_fitness_function(network):
    connectivity_components = network.graph.get_connectivity_components()
    return max(map(lambda item: len(item[1]), connectivity_components.items()))


interest_areas = generate_interest_areas()

if RUN_GA:
    # GA - will always mutate (mutation factor = 1)
    ga = GA(interest_areas=interest_areas, initial_population_size=20, generations=200,
            fitness_function=largest_connectivity_componenet_fitness_function, mutation_factor=1)
    fig_id = 1
    # for agent in ga.agents:
    #     network = agent.network
    #     network.plot(fig_id=fig_id, xlims=[-7, 7], ylims=[-7, 7])
    #     fig_id += 1
    ga.evolve()
    agents = sorted(ga.agents, key=lambda agent: agent.fitness, reverse=True)
    network = agents[0].network
    network.plot(fig_id=fig_id, xlims=[-7, 7], ylims=[-7, 7])
    ga.statistics.plot_statistic(name=GAStatistics.GEN_FITNESS)
    ga.statistics.plot_statistic(name=GAStatistics.GEN_TIME)
else:
    plt.figure(1)
    ax = plt.gca()
    for ia in interest_areas:
        color = 'blue' if not ia.is_hub else 'green'
        c = CircleUI((ia.center.x, ia.center.y), ia.radius, facecolor=color, edgecolor='black')
        c.set_alpha(0.5)
        c.set_label(ia)
        ax.add_artist(c)
    ax.set_title('Adhoc Network')
    plt.xlim(X_LIMS[0], X_LIMS[1])
    plt.ylim(Y_LIMS[0], Y_LIMS[1])
    plt.show()

import random
from network import InterestArea
from geometry import Point
from ga import GA, GAStatistics


def generate_interest_areas(num_of_interest_areas, xlims, ylims, allow_overlapping=False):
    interest_areas = set()
    interest_area_id = 1
    while len(interest_areas) < num_of_interest_areas:
        ia = InterestArea(center=Point(x=(xlims[0] + 1) + (xlims[1] - 1 - xlims[0] - 1) * random.random(),
                                       y=(ylims[0] + 1) + (ylims[1] - 1 - ylims[0] - 1) * random.random()),
                          radius=0.5, name='Omega' + str(interest_area_id))
        if not allow_overlapping:
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
    return max(map(lambda item: len(item[1]), connectivity_components.items())) + len(network.graph.edges)


def main(*args, **kwargs):
    population_size = kwargs.get('initial_population_size')
    generations = kwargs.get('max_generations')

    num_of_interest_areas = kwargs.get('num_of_interest_reas')
    xlims = kwargs.get('xlims')
    ylims = kwargs.get('ylims')

    interest_areas = generate_interest_areas(num_of_interest_areas=num_of_interest_areas, xlims=xlims, ylims=ylims)

    # GA - will always mutate (mutation factor = 1)
    ga = GA(interest_areas=interest_areas, initial_population_size=population_size, generations=generations,
            fitness_function=largest_connectivity_componenet_fitness_function, mutation_factor=1)
    fig_id = 1
    # for agent in ga.agents:
    #     network = agent.network
    #     network.plot(fig_id=fig_id, xlims=[-7, 7], ylims=[-7, 7])
    #     fig_id += 1
    ga.evolve()
    fittest_agent = ga.get_fittest()
    network = fittest_agent.network
    network.plot(fig_id=fig_id, xlims=kwargs.get('xlims'), ylims=kwargs.get('ylims'))
    ga.statistics.plot_statistic(name=GAStatistics.GEN_FITNESS)
    ga.statistics.plot_statistic(name=GAStatistics.GEN_TIME)


if __name__ == '__main__':
    x_lims = (-7, 7)
    y_lims = (-7, 7)
    amount_of_interest_areas = 100

    initial_population_size = 20
    max_generations = 300

    main(initial_population_size=initial_population_size, max_generations=max_generations,
         num_of_interest_reas=amount_of_interest_areas, xlims=x_lims, ylims=y_lims)

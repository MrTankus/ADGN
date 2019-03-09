import random
import datetime
from network import InterestArea
from geometry import Point
from ga import GA, GAStatistics

test_interest_areas = [
    InterestArea(center=Point(0, 0), radius=0.5, name='HUB', is_hub=True),
    InterestArea(center=Point(1, 0.5), radius=0.5, name='Omega1'),
    InterestArea(center=Point(2, 0), radius=0.5, name='Omeg2'),
    InterestArea(center=Point(1, -0.5), radius=0.5, name='Omega3'),
]


def generate_interest_areas(num_of_interest_areas, xlims, ylims, allow_overlapping=False):
    interest_areas = set()
    interest_area_id = 1
    while len(interest_areas) < num_of_interest_areas:
        ia = InterestArea(center=Point(x=(xlims[0] + 1) + (xlims[1] - 1 - xlims[0] - 1) * random.random(),
                                       y=(ylims[0] + 1) + (ylims[1] - 1 - ylims[0] - 1) * random.random()),
                          radius=0.3 + 0.2 * random.random(), name='Omega' + str(interest_area_id))
        if not allow_overlapping:
            if not any(other.intersects(ia) for other in interest_areas):
                interest_areas.add(ia)

    hub = random.sample(interest_areas, 1)[0]
    hub.name = 'HUB'
    hub.is_hub = True

    return interest_areas


def edges_fitness_function(network):
    return len(network.graph.edges)


def largest_connectivity_componenet_fitness_function(network):
    connectivity_components = network.graph.get_connectivity_components()
    return max(map(lambda cc_index: len(connectivity_components[cc_index]), connectivity_components)) + len(network.graph.edges)


def main(*args, **kwargs):
    population_size = kwargs.get('initial_population_size')
    generations = kwargs.get('max_generations')

    num_of_interest_areas = kwargs.get('num_of_interest_reas')
    xlims = kwargs.get('xlims')
    ylims = kwargs.get('ylims')

    print('Generating random interest areas')
    # interest_areas = test_interest_areas
    interest_areas = generate_interest_areas(num_of_interest_areas=num_of_interest_areas, xlims=xlims, ylims=ylims)

    # GA - will always mutate (mutation factor = 1)
    ga = GA(interest_areas=interest_areas, initial_population_size=population_size, generations=generations,
            fitness_function=largest_connectivity_componenet_fitness_function, mutation_factor=1)

    # Fittest member in initial population
    fittest_agent = ga.get_fittest()
    network = fittest_agent.network
    network.plot(fig_id=1, title='initial fittest', xlims=kwargs.get('xlims'), ylims=kwargs.get('ylims'))

    # Run GA
    start = datetime.datetime.now()
    ga.evolve()
    end = datetime.datetime.now() - start
    print("GA took {} seconds to complete".format(end.total_seconds()))

    # Fittest member in evolved population
    fittest_agent = ga.get_fittest()
    network = fittest_agent.network
    network.plot(fig_id=1, title='final fittest', xlims=kwargs.get('xlims'), ylims=kwargs.get('ylims'))

    # Plotting statistics
    ga.statistics.plot_statistic(name=GAStatistics.GEN_FITNESS)
    ga.statistics.plot_statistic(name=GAStatistics.GEN_TIME)


if __name__ == '__main__':
    x_lims = (-6, 6)
    y_lims = (-6, 6)
    amount_of_interest_areas = 100

    initial_population_size = 20
    max_generations = 500

    main(initial_population_size=initial_population_size, max_generations=max_generations,
         num_of_interest_reas=amount_of_interest_areas, xlims=x_lims, ylims=y_lims)

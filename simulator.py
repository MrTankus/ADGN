import random
import datetime
from multiprocessing.pool import Pool

from analysis.network_analysis import check_resilience
from analysis.fitness_functions import sum_square_connectivity_componenet_fitness_function, avg_on_paths_length_fitness_function
from network import InterestArea
from ga.ga import GA
from ga.statistics import GAStatistics
from utils import plot_network, plot_statistics

test_interest_areas = [
    InterestArea(center=(0, 0), radius=0.5, name='HUB', is_hub=True),
    InterestArea(center=(1, 0.5), radius=0.5, name='Omega1'),
    InterestArea(center=(2, 0), radius=0.5, name='Omeg2'),
    InterestArea(center=(1, -0.5), radius=0.5, name='Omega3'),
    InterestArea(center=(2, -1.8), radius=0.5, name='Omega4'),
]


def generate_interest_areas(num_of_interest_areas, xlims, ylims, allow_overlapping=False):
    interest_areas = set()
    interest_area_id = 1
    while len(interest_areas) < num_of_interest_areas:
        ia = InterestArea(center=((xlims[0] + 1) + (xlims[1] - 1 - xlims[0] - 1) * random.random(),
                                  (ylims[0] + 1) + (ylims[1] - 1 - ylims[0] - 1) * random.random()),
                          radius=0.3 + 0.2 * random.random(), name='IA-' + str(interest_area_id))
        if not allow_overlapping:
            if not any(other.intersects(ia) for other in interest_areas):
                interest_areas.add(ia)
                interest_area_id += 1
        else:
            interest_areas.add(ia)
            interest_area_id += 1

    hub = random.sample(interest_areas, 1)[0]
    hub.name = 'HUB'
    hub.is_hub = True

    return interest_areas


def main(*args, **kwargs):
    population_size = kwargs.get('initial_population_size')
    generations = kwargs.get('max_generations')

    num_of_interest_areas = kwargs.get('num_of_interest_reas')
    xlims = kwargs.get('xlims')
    ylims = kwargs.get('ylims')

    print('Generating random interest areas')
    # interest_areas = test_interest_areas
    interest_areas = generate_interest_areas(num_of_interest_areas=num_of_interest_areas, xlims=xlims, ylims=ylims,
                                             allow_overlapping=False)

    # GA - will always mutate (mutation factor = 1)

    ga = GA(interest_areas=interest_areas, initial_population_size=population_size, generations=generations,
            fitness_function=avg_on_paths_length_fitness_function, mutation_factor=1)

    ga.generate_initial_population()
    start = datetime.datetime.now()

    if kwargs.get('parallel', False):
        with Pool() as pool:
            ga.evolve(pool=pool)
    else:
        ga.evolve()

    end = datetime.datetime.now() - start
    print("GA took {} seconds to complete".format(end.total_seconds()))
    # Fittest member in evolved population
    fittest_agent = ga.get_fittest()
    network = fittest_agent.network
    plot_network(network=ga.initial_fittest.network, title='initial fittest', xlims=kwargs.get('xlims'), ylims=kwargs.get('ylims'))
    plot_network(network=network, title='final fittest', xlims=kwargs.get('xlims'), ylims=kwargs.get('ylims'))

    # Plotting statistics
    plot_statistics(statistic=ga.statistics.statistics.get(GAStatistics.GEN_FITNESS), name=GAStatistics.GEN_FITNESS)
    plot_statistics(statistic=ga.statistics.statistics.get(GAStatistics.GEN_TIME), name=GAStatistics.GEN_TIME)
    plot_statistics(name='Resilience', statistic=check_resilience(network=network),
                    generate_ys=lambda xs: list(map(lambda x: x, xs)))


if __name__ == '__main__':
    s = 6
    x_lims = (-s, s)
    y_lims = (-s, s)
    amount_of_interest_areas = 50

    initial_population_size = 20
    max_generations = 200

    main(initial_population_size=initial_population_size, max_generations=max_generations,
         num_of_interest_reas=amount_of_interest_areas, xlims=x_lims, ylims=y_lims, parallel=True)

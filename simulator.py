import hashlib
import json
import uuid

from ga.v2.statistics import GAStatistics
from network.v2.interest_areas import InterestAreaGenerator
from analysis.v2.fitness_functions import FitnessFunctions
from ga.v2.ga import GA
from utils.v2.utils import save_network_image, save_statistics, timer


def main(*args, **kwargs):
    fitness_function_name = FitnessFunctions.HARMONIC_AVG_PATH_LENGTH
    run_id = '{}_{}'.format(fitness_function_name, hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:8])
    population_size = kwargs.get('initial_population_size')
    generations = kwargs.get('max_generations')

    num_of_interest_areas = kwargs.get('num_of_interest_reas')
    xlims = kwargs.get('xlims')
    ylims = kwargs.get('ylims')

    print('Generating random interest areas')
    interest_areas = None
    if kwargs.get('load_interest_areas'):
        interest_areas = InterestAreaGenerator.from_file('ia.json')
    if not interest_areas:
        interest_areas = InterestAreaGenerator.random(amount=num_of_interest_areas, xlims=xlims, ylims=ylims,
                                                      allow_overlapping=False)

        with open('ia.json', 'w') as file:
            file.write(json.dumps([
                ia.as_json_dict() for ia in interest_areas
            ]))

    # GA - will always mutate (mutation factor = 1)
    fitness_function = FitnessFunctions.get_fitness_function(fitness_function_name)
    ga = GA(interest_areas=interest_areas, initial_population_size=population_size, generations=generations,
            fitness_function=fitness_function, mutation_factor=1, run_id=run_id,
            optimum=FitnessFunctions.get_fitness_function_optimum(fitness_function_name))

    ga.generate_initial_population()

    with timer(op_name='evolution'):
        ga.evolve()

    print("Creating statistics graphs")
    save_statistics(GAStatistics.GEN_FITNESS, ga.statistics.get(GAStatistics.GEN_FITNESS),
                    path='simulations/{}/{}.png'.format(run_id, GAStatistics.GEN_FITNESS))

    print("Creating network evolution visualization")
    ga.generate_evolution_visualization(network_image_saver=save_network_image)
    print("Finished!")


if __name__ == '__main__':
    s = 8
    x_lims = (-s, s)
    y_lims = (-s, s)
    amount_of_interest_areas = 50

    initial_population_size = 50
    max_generations = 1000
    ga_iterations = 1

    for _ in range(ga_iterations):
        print('================================ STARTING {} RUN ================================'.format(_))
        main(initial_population_size=initial_population_size, max_generations=max_generations,
             num_of_interest_reas=amount_of_interest_areas, xlims=x_lims, ylims=y_lims, save=False,
             load_interest_areas=True)
        print('================================ FINISHED {} RUN ================================'.format(_))


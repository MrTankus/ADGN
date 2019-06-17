import datetime
import hashlib
import json
import uuid

import imageio

from multiprocessing.pool import Pool

from network.v2.interest_areas import InterestArea, InterestAreaGenerator
from analysis.v2.fitness_functions import FitnessFunctions
from ga.v2.ga import GA
from utils.v2.utils import save_network_image

test_interest_areas = [
    InterestArea(center=(0, 0), radius=0.5, name='HUB', is_hub=True),
    InterestArea(center=(1, 0.5), radius=0.5, name='Omega1'),
    InterestArea(center=(2, 0), radius=0.5, name='Omeg2'),
    InterestArea(center=(1, -0.5), radius=0.5, name='Omega3'),
    InterestArea(center=(2, -1.8), radius=0.5, name='Omega4'),

    InterestArea(center=(5, 4), radius=0.5, name='Omega5'),
    InterestArea(center=(3.5, 4.1), radius=0.5, name='Omega6'),
]


def main(*args, **kwargs):
    run_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:8]
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
    fitness_function = FitnessFunctions.get_fitness_function(FitnessFunctions.SUM_SQUARE_CC_SIZE)
    ga = GA(interest_areas=interest_areas, initial_population_size=population_size, generations=generations,
            fitness_function=fitness_function, mutation_factor=1, network_image_saver=save_network_image, run_id=run_id)

    ga.generate_initial_population()
    start = datetime.datetime.now()

    if kwargs.get('parallel', False):
        with Pool() as pool:
            ga.evolve(pool=pool)
    else:
        ga.evolve()

    end = datetime.datetime.now() - start
    print("GA took {} seconds to complete".format(end.total_seconds()))
    print("Creating gif of network evolution")
    images = []
    for image in ga.gif_images:
        images.append(imageio.imread(image))
    imageio.mimsave('simulations/{}/network_evolution.gif'.format(run_id), images, duration=0.2)
    print("Finished!")


if __name__ == '__main__':
    s = 8
    x_lims = (-s, s)
    y_lims = (-s, s)
    amount_of_interest_areas = 50

    initial_population_size = 20
    max_generations = 500

    main(initial_population_size=initial_population_size, max_generations=max_generations,
         num_of_interest_reas=amount_of_interest_areas, xlims=x_lims, ylims=y_lims, parallel=False, save=False,
         load_interest_areas=False)

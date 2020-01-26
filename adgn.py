import argparse
import hashlib
import json

from jsonschema import validate
import logging
from pathlib import Path
import uuid
from sys import stdout

from analysis.v2.fitness_functions import FitnessFunctions
from ga.v2.ga import GA, ParallelGA
from ga.v2.statistics import GAStatistics
from network.v2.interest_areas import InterestAreaGenerator
from utils.v2.utils import timer, save_statistics, save_network_image, str2bool

logger = logging.getLogger('AGDN')
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler = logging.StreamHandler(stdout)
handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def main():
    parser = argparse.ArgumentParser(description='Create an optimized adhoc sensor network')
    parser.add_argument('--interest-areas', dest='interest_areas', required=True,
                        help='a path to the interest areas json file')
    parser.add_argument('--fitness-function', dest='fitness_function', required=True, type=int,
                        help='1 (sum square cc size)  or 3 (harmonic avg path length)')
    parser.add_argument('--output-base-dir', dest='output_dir', required=True,
                        help='The output folder path. The GA process will write there files for visualization of optimized network')
    parser.add_argument('--initial-population', dest='initial_population', required=False, type=int, default=10,
                        help='The size of the initial population for the GA')
    parser.add_argument('--generations', dest='generations', required=False, type=int, default=300,
                        help='The number of generations for evolution.')
    parser.add_argument('--mutation-factor', dest='mutation_factor', required=False, type=float, default=1,
                        help='The probability of mutation')

    parser.add_argument('--parallel', dest='parallel', required=False, type=str2bool, default=False,
                        help='How many processes to spawn for parallel calculation')

    args = parser.parse_args()

    logger.info('validating and loading interest areas from %s', args.interest_areas)
    interest_areas = load_interest_areas(args.interest_areas)
    fitness_function = FitnessFunctions.get_fitness_function(args.fitness_function)
    run_id = '{}_{}'.format(args.fitness_function, hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:8])

    logger.info('creating initial population of size %s', args.initial_population)
    with timer(op_name='evolution', logger=logger):
        if not args.parallel:
            logger.info("starting GA process synchronously")
            ga = GA(interest_areas=interest_areas, initial_population_size=args.initial_population,
                    generations=args.generations, fitness_function=fitness_function,
                    optimum=FitnessFunctions.get_fitness_function_optimum(args.fitness_function),
                    mutation_factor=args.mutation_factor, run_id=run_id)
            ga.generate_initial_population()
            ga.evolve(logger=logger)
        else:
            logger.info("starting GA process asynchronously")
            from multiprocessing.pool import Pool
            with Pool() as pool:
                ga = ParallelGA(interest_areas=interest_areas, initial_population_size=args.initial_population,
                                generations=args.generations, fitness_function=fitness_function,
                                optimum=FitnessFunctions.get_fitness_function_optimum(args.fitness_function), pool=pool,
                                mutation_factor=args.mutation_factor, run_id=run_id,)
                ga.generate_initial_population()
                ga.evolve(logger=logger)

    create_ga_process_visualization(ga=ga, output_dir=args.output_dir)
    logger.info('Finished GA process')


def load_interest_areas(interest_areas_definition):
    with open(interest_areas_definition, 'r') as interes_areas_file, open('schemas/interest_areas_schema.json', 'r') as interest_areas_schema_file:
        interest_areas_json = json.loads(interes_areas_file.read())
        interest_areas_schema = json.loads(interest_areas_schema_file.read())
        validate(interest_areas_json, interest_areas_schema)
    return InterestAreaGenerator.from_file(interest_areas_definition)


def create_ga_process_visualization(ga, output_dir):
    logger.info('creating statistical data visualization')
    Path('{}/{}/snapshots'.format(output_dir, ga.run_id)).mkdir(parents=True, exist_ok=True)
    save_statistics(GAStatistics.GEN_FITNESS, ga.statistics.get(GAStatistics.GEN_FITNESS),
                    path='{}/{}/{}.png'.format(output_dir, ga.run_id, GAStatistics.GEN_FITNESS))

    logger.info('creating evolution visualization')
    ga.generate_evolution_visualization(network_image_saver=save_network_image, output_dir=output_dir)


if __name__ == '__main__':
    main()



import argparse
import hashlib
import json

from jsonschema import validate
import logging
from pathlib import Path
import uuid
from sys import stdout

from analysis.fitness_functions import FitnessFunctions
from optimization.ga import GA, ParallelGA
from optimization.sgd import SGD
from optimization.statistics import GAStatistics
from network.interest_areas import InterestAreaGenerator
from utils.utils import timer, save_statistics, save_network_image, str2bool

formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler = logging.StreamHandler(stdout)
handler.setFormatter(formatter)
logger = logging.getLogger('AGDN')
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def main():
    parser = argparse.ArgumentParser(description='Create an optimized adhoc sensor network')
    parser.add_argument('--interest-areas', dest='interest_areas', required=True,
                        help='a path to the interest areas json file')
    parser.add_argument('--fitness-function', dest='fitness_function', required=True, type=int,
                        help='1 (sum square cc size)  or 3 (harmonic avg path length)')
    parser.add_argument('--output-base-dir', dest='output_dir', required=True,
                        help='The GA process output folder path. (process visualization and result)')
    parser.add_argument('--iterations', dest='iterations', required=False, type=int, default=300,
                        help='The number of iterations for evolution.')
    parser.add_argument('--initial-population', dest='initial_population', required=False, type=int, default=10,
                        help='The size of the initial population for the GA')
    parser.add_argument('--mutation-factor', dest='mutation_factor', required=False, type=float, default=1,
                        help='The probability of mutation')
    parser.add_argument('--visualize', dest='visualize', required=False, type=str2bool, default=False,
                        help='How many processes to spawn for parallel calculation')
    parser.add_argument('--parallel', dest='parallel', required=False, type=str2bool, default=False,
                        help='How many processes to spawn for parallel calculation')
    parser.add_argument('--optimization-method', dest='optimization_method', required=False, default='ga')

    args = parser.parse_args()

    logger.info('validating and loading interest areas from %s', args.interest_areas)
    interest_areas = load_interest_areas(args.interest_areas)
    fitness_function = FitnessFunctions.get_fitness_function(args.fitness_function)
    run_id = '{}_{}'.format(args.fitness_function, hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:8])

    if args.optimization_method == 'ga':
        logger.info('creating initial population of size %s', args.initial_population)
        with timer(op_name='evolution', logger=logger):
            if args.parallel:
                logger.info("starting GA process (%s) asynchronously", run_id)
                from multiprocessing.pool import Pool
                with Pool() as pool:
                    ga = ParallelGA(interest_areas=interest_areas, initial_population_size=args.initial_population,
                                    generations=args.iterations, fitness_function=fitness_function,
                                    optimum=FitnessFunctions.get_fitness_function_optimum(args.fitness_function), pool=pool,
                                    mutation_factor=args.mutation_factor, run_id=run_id)
                    ga.generate_initial_population()
                    ga.evolve(logger=logger)
            else:
                logger.info("starting GA process (%s) synchronously", run_id)
                ga = GA(interest_areas=interest_areas, initial_population_size=args.initial_population,
                        generations=args.iterations, fitness_function=fitness_function,
                        optimum=FitnessFunctions.get_fitness_function_optimum(args.fitness_function),
                        mutation_factor=args.mutation_factor, run_id=run_id)

                ga.generate_initial_population()
                ga.evolve(logger=logger)

        create_ga_process_files(process=ga, output_dir=args.output_dir, visualize_ga=args.visualize)
    elif args.optimization_method == 'sgd':
        sgd = SGD(run_id=run_id, interest_areas=interest_areas, fitness_function=fitness_function,
                  optimum=FitnessFunctions.get_fitness_function_optimum(args.fitness_function), iterations=args.iterations)
        sgd.evolve(logger=logger)
        create_ga_process_files(process=sgd, output_dir=args.output_dir, visualize_ga=args.visualize)
    else:
        logger.error('Unknown optimization method %s. Please use GA or SGD', args.optimization_method)
    logger.info('Finished optimization process')


def load_interest_areas(interest_areas_definition):
    with open(interest_areas_definition, 'r') as interes_areas_file, open('schemas/interest_areas_schema.json', 'r') as interest_areas_schema_file:
        interest_areas_json = json.loads(interes_areas_file.read())
        interest_areas_schema = json.loads(interest_areas_schema_file.read())
        validate(interest_areas_json, interest_areas_schema)
    return InterestAreaGenerator.from_file(interest_areas_definition)


def create_ga_process_files(process, output_dir, visualize_ga=False):
    logger.info('creating optimization process files')
    Path('{}/{}'.format(output_dir, process.run_id)).mkdir(parents=True, exist_ok=True)
    fittest_network = process.get_fittest().network
    with open('{}/{}/network.json'.format(output_dir, process.run_id), 'w+') as network_file:
        network_file.write(json.dumps(fittest_network.as_json_dict(with_edges=True)))
    with open('{}/{}/network.info'.format(output_dir, process.run_id), 'w+') as network_info_file:
        network_info = {
            'connectivity_components_amount': len(fittest_network.graph.get_connectivity_components()),
            'size_of_largest_component': max([len(cc) for cc in fittest_network.graph.get_connectivity_components()]),
        }
        network_info_file.write(json.dumps(network_info))
    if process.statistics:
        logger.info("creating statistics visualization")
        save_statistics(GAStatistics.GEN_FITNESS, process.statistics.get(GAStatistics.GEN_FITNESS),
                        path='{}/{}/{}.png'.format(output_dir, process.run_id, GAStatistics.GEN_FITNESS))
    if visualize_ga:
        Path('{}/{}/snapshots'.format(output_dir, process.run_id)).mkdir(parents=True, exist_ok=True)
        logger.info('creating optimization visualization')
        process.generate_evolution_visualization(network_image_saver=save_network_image, output_dir=output_dir)


if __name__ == '__main__':
    main()



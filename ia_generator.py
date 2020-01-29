import argparse
import json
import logging

from sys import stdout

from network.interest_areas import InterestAreaGenerator
from utils.utils import plot_interest_areas, str2bool

formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
handler = logging.StreamHandler(stdout)
handler.setFormatter(formatter)
logger = logging.getLogger('IA_GENERATOR')
logger.setLevel(logging.INFO)
logger.addHandler(handler)


def main():
    parser = argparse.ArgumentParser(description='Create an optimized adhoc sensor network')
    parser.add_argument('--amount', dest='interest_areas_amount', required=True, type=int,
                        help='The amount of interest areas')

    parser.add_argument('--xlim', dest='xlim', required=True, type=float,
                        help='limit on x axis')

    parser.add_argument('--ylim', dest='ylim', required=True, type=float,
                        help='limit on y axis')

    parser.add_argument('--output', dest='output', required=True, type=str,
                        help='the output file (with path) to generate the interest areas json file')

    parser.add_argument('--allow-overlap', dest='allow_overlap', required=False, default=False, type=str2bool,
                        help='can interest areas overlap')

    parser.add_argument('--show', dest='show', required=False, default=True, type=str2bool,
                        help='show the generated interest areas')

    args = parser.parse_args()
    xlims = (-args.xlim, args.xlim)
    ylims = (-args.ylim, args.ylim)
    logger.info("generating %s random interest areas in %s X %s", args.interest_areas_amount, xlims, ylims)
    interest_areas = InterestAreaGenerator.random(amount=args.interest_areas_amount, xlims=xlims,
                                                  ylims=ylims, allow_overlapping=args.allow_overlap)

    logger.info("writing to %s", args.output)
    with open(args.output, 'w') as file:
        file.write(json.dumps([
            ia.as_json_dict() for ia in interest_areas
        ]))

    if args.show:
        logger.info("showing result")
        plot_interest_areas(interest_areas=interest_areas, xlims=xlims, ylims=ylims)


if __name__ == '__main__':
    main()

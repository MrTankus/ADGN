import argparse
import json

from network.interest_areas import InterestAreaGenerator
from utils.utils import plot_interest_areas, str2bool


def main():
    parser = argparse.ArgumentParser(description='Create an optimized adhoc sensor network')
    parser.add_argument('--amount', dest='interest_areas_amount', required=True, type=int,
                        help='The amount of interest areas')

    parser.add_argument('--xlim', dest='xlim', required=True, type=float,
                        help='limit on x axis')

    parser.add_argument('--ylim', dest='ylim', required=True, type=float,
                        help='limit on y axis')

    parser.add_argument('--allow-overlap', dest='allow_overlap', required=False, default=False, type=str2bool,
                        help='can interest areas overlap')

    parser.add_argument('--show', dest='show', required=False, default=True, type=str2bool,
                        help='show the generated interest areas')

    args = parser.parse_args()

    interest_areas = InterestAreaGenerator.random(amount=args.interest_areas_amount, xlims=(-args.xlim, args.xlim),
                                                  ylims=(-args.ylim, args.ylim), allow_overlapping=args.allow_overlap)

    with open('ia.json', 'w') as file:
        file.write(json.dumps([
            ia.as_json_dict() for ia in interest_areas
        ]))

    if args.show:
        plot_interest_areas(interest_areas=interest_areas, xlims=(-args.xlim, args.xlim), ylims=(-args.ylim, args.ylim))


if __name__ == '__main__':
    main()

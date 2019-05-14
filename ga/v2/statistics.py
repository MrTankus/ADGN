
from collections import defaultdict


class GAStatistics(object):

    GEN_FITNESS = 'Gen-Fitness'
    GEN_TIME = 'Gen-Time'

    def __init__(self, ga):
        self.ga = ga
        self.statistics = defaultdict(list)

    def gen_snapshot(self, gen, time_spent):
        self.statistics[GAStatistics.GEN_FITNESS].append((gen, self.ga.get_fittest().fitness))
        self.statistics[GAStatistics.GEN_TIME].append((gen, time_spent))

    def get(self, name):
        return self.statistics.get(name)

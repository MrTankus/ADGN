import math


def euclidean_metric(p1, p2):
    return math.sqrt(sum(map(lambda c1, c2: (c1 - c2) ** 2, p1, p2)))

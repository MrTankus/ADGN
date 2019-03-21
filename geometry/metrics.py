import math


def euclidean_metric(p1, p2):
    return math.sqrt(sum(map(lambda p: (p[0] - p[1]) ** 2, zip(p1, p2))))

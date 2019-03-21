import itertools
import math
import numpy as np

from geometry.metrics import euclidean_metric


class LineSegment(object):

    def __init__(self, p1, p2, metric=euclidean_metric):
        self.p1 = p1
        self.p2 = p2
        self.length = metric(self.p1, self.p2)
        self.slope = math.inf
        if self.p1[0] != self.p2[0]:
            self.slope = (self.p1[1] - self.p2[1]) / (self.p1[0] - self.p2[0])

        x_mid = (self.p1[0] + self.p2[0]) / 2
        y_mid = (self.p1[1] + self.p2[1]) / 2
        self.mid_point = (x_mid, y_mid)
        self._hash = hash(frozenset({self.p1, self.p2}))

    def __eq__(self, other):
        return (self.p1 == other.p1 and self.p2 == other.p2) or (self.p2 == other.p1 and self.p1 == other.p2)

    def __hash__(self):
        return self._hash

    def is_parallel(self, line_segment):
        return self.slope == line_segment.slope

    def get_intersection_point(self, line_segment):
        if self.is_parallel(line_segment=line_segment):
            return None
        else:
            x_numerator = np.linalg.det(
                [
                    [
                        np.linalg.det([[self.p1[0], self.p1[1]], [self.p2[0], self.p2[1]]]),
                        np.linalg.det([[self.p1[0], 1], [self.p2[0], 1]])
                    ],
                    [
                        np.linalg.det([[line_segment.p1[0], line_segment.p1[1]], [line_segment.p2[0], line_segment.p2[1]]]),
                        np.linalg.det([[line_segment.p1[0], 1], [line_segment.p2[0], 1]])
                    ]
                ]
            )

            y_numerator = np.linalg.det(
                [
                    [
                        np.linalg.det([[self.p1[0], self.p1[1]], [self.p2[0], self.p2[1]]]),
                        np.linalg.det([[self.p1[1], 1], [self.p2[1], 1]])
                    ],
                    [
                        np.linalg.det([[line_segment.p1[0], line_segment.p1[1]], [line_segment.p2[0], line_segment.p2[1]]]),
                        np.linalg.det([[line_segment.p1[1], 1], [line_segment.p2[1], 1]])
                    ]
                ]
            )

            denominator = np.linalg.det(
                [
                    [
                        np.linalg.det([[self.p1[0], 1], [self.p2[0], 1]]),
                        np.linalg.det([[self.p1[1], 1], [self.p2[1], 1]])
                    ],
                    [
                        np.linalg.det([[line_segment.p1[0], 1], [line_segment.p2[0], 1]]),
                        np.linalg.det([[line_segment.p1[1], 1], [line_segment.p2[1], 1]])
                    ]
                ]
            )

            return (x_numerator / denominator), (y_numerator / denominator)


class Circle(object):

    def __init__(self, center, radius, metric=euclidean_metric):
        self.center = center
        self.radius = radius
        self.metric = metric

    def __eq__(self, other):
        return self.center == other.center and self.radius == other.radius

    def __hash__(self):
        return hash((self.center, self.radius))

    def is_in_circle(self, point):
        return self.metric(self.center, point) <= self.radius

    def intersects(self, circle):
        return self.metric(self.center, circle.center) < (self.radius + circle.radius)

    @classmethod
    def get_point_in_intersection(cls, circles):
        circles_pairs = itertools.combinations(circles, 2)
        all_intersection_points = set()

        lines = []
        for c1, c2 in circles_pairs:
            intersection_points = c1.get_intersection_points(circle=c2)
            if intersection_points:
                all_intersection_points.add(intersection_points[0])
                all_intersection_points.add(intersection_points[1])
                lines.append(LineSegment(p1=intersection_points[0], p2=intersection_points[1]))

        if len(lines) == 1:
            return all_intersection_points, lines[0].mid_point
        else:
            points = set()
            line_pairs = itertools.combinations(lines, 2)
            for l1, l2 in line_pairs:
                p = l1.get_intersection_point(line_segment=l2)
                if p:
                    points.add(p)
            if len(points) >= 3:
                return all_intersection_points, (ConvexHull(points)).get_center()

        raise Exception('problem while calculating intersection shape')

    def get_intersection_points(self, circle):
        if self == circle:
            return None
        if not self.intersects(circle=circle):
            return []

        d = self.metric(self.center, circle.center)
        a = ((self.radius ** 2) - (circle.radius ** 2) + (d ** 2)) / (2 * d)
        h = math.sqrt((self.radius ** 2) - (a ** 2))
        mid_point_x = self.center[0] + a * (circle.center[0] - self.center[0]) / d
        mid_point_y = self.center[1] + a * (circle.center[1] - self.center[1]) / d

        intersection_p1_x = mid_point_x + (h * (circle.center[1] - self.center[1]) / d)
        intersection_p1_y = mid_point_y - (h * (circle.center[0] - self.center[0]) / d)

        intersection_p2_x = mid_point_x - (h * (circle.center[1] - self.center[1]) / d)
        intersection_p2_y = mid_point_y + (h * (circle.center[0] - self.center[0]) / d)
        return [(intersection_p1_x, intersection_p1_y), (intersection_p2_x, intersection_p2_y)]


class ConvexHull(object):

    def __init__(self, points):
        self.points = points
        self.center = None

    def get_center(self):
        if not self.center:
            x_avg = sum([p[0] for p in self.points]) / len(self.points)
            y_avg = sum([p[1] for p in self.points]) / len(self.points)
            self.center = (x_avg, y_avg)
        return self.center

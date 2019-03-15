import itertools
import numbers
import math
import numpy as np


class Point(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return str((self.x, self.y))

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return Point(self.x * other, self.y * other)
        raise TypeError('Unsupported operand types for *')

    def distance(self, point):
        return math.sqrt(((self.x - point.x) ** 2) + ((self.y - point.y) ** 2))

    def as_list(self):
        return [self.x, self.y]

    def clone(self):
        return Point(x=self.x, y=self.y)


class LineSegment(object):

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        self.length = self.p1.distance(self.p2)
        self.slope = math.inf
        if self.p1.x != self.p2.x:
            self.slope = (self.p1.y - self.p2.y) / (self.p1.x - self.p2.x)

        x_mid = (self.p1.x + self.p2.x) / 2
        y_mid = (self.p1.y + self.p2.y) / 2
        self._mid_point = Point(x=x_mid, y=y_mid)
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
                        np.linalg.det([[self.p1.x, self.p1.y], [self.p2.x, self.p2.y]]),
                        np.linalg.det([[self.p1.x, 1], [self.p2.x, 1]])
                    ],
                    [
                        np.linalg.det([[line_segment.p1.x, line_segment.p1.y], [line_segment.p2.x, line_segment.p2.y]]),
                        np.linalg.det([[line_segment.p1.x, 1], [line_segment.p2.x, 1]])
                    ]
                ]
            )

            y_numerator = np.linalg.det(
                [
                    [
                        np.linalg.det([[self.p1.x, self.p1.y], [self.p2.x, self.p2.y]]),
                        np.linalg.det([[self.p1.y, 1], [self.p2.y, 1]])
                    ],
                    [
                        np.linalg.det([[line_segment.p1.x, line_segment.p1.y], [line_segment.p2.x, line_segment.p2.y]]),
                        np.linalg.det([[line_segment.p1.y, 1], [line_segment.p2.y, 1]])
                    ]
                ]
            )

            denominator = np.linalg.det(
                [
                    [
                        np.linalg.det([[self.p1.x, 1], [self.p2.x, 1]]),
                        np.linalg.det([[self.p1.y, 1], [self.p2.y, 1]])
                    ],
                    [
                        np.linalg.det([[line_segment.p1.x, 1], [line_segment.p2.x, 1]]),
                        np.linalg.det([[line_segment.p1.y, 1], [line_segment.p2.y, 1]])
                    ]
                ]
            )

            return Point(x=(x_numerator / denominator), y=(y_numerator / denominator))

    def get_mid_point(self):
        return Point(x=self._mid_point.x, y=self._mid_point.y)


class Circle(object):

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def __eq__(self, other):
        return self.center == other.center and self.radius == other.radius

    def __hash__(self):
        return hash((self.center, self.radius))

    def is_in_circle(self, point):
        return self.center.distance(point=point) <= self.radius

    def intersects(self, circle):
        return self.center.distance(circle.center) < (self.radius + circle.radius)

    def get_intersection_points(self, circle):
        if self == circle:
            return None
        d = self.center.distance(point=circle.center)
        if not self.intersects(circle=circle):
            return []
        a = ((self.radius ** 2) - (circle.radius ** 2) + (d ** 2)) / (2 * d)
        h = math.sqrt((self.radius ** 2) - (a ** 2))
        mid_point = self.center + ((circle.center - self.center) * (a / d))

        intersection_p1_x = mid_point.x + (h * (circle.center.y - self.center.y) / d)
        intersection_p1_y = mid_point.y - (h * (circle.center.x - self.center.x) / d)

        intersection_p2_x = mid_point.x - (h * (circle.center.y - self.center.y) / d)
        intersection_p2_y = mid_point.y + (h * (circle.center.x - self.center.x) / d)
        return [Point(x=intersection_p1_x, y=intersection_p1_y), Point(x=intersection_p2_x, y=intersection_p2_y)]

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
            return all_intersection_points, lines[0].get_mid_point()
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


class ConvexHull(object):

    def __init__(self, points):
        self.points = points
        self.center = None

    def get_center(self):
        if not self.center:
            x_avg = sum([p.x for p in self.points]) / len(self.points)
            y_avg = sum([p.y for p in self.points]) / len(self.points)
            self.center = Point(x=x_avg, y=y_avg)
        return self.center

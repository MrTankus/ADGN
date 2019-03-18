
class Edge(object):

    def __init__(self, node1, node2, cost_function=None):
        assert cost_function is None or callable(cost_function)
        self.node1 = node1
        self.node2 = node2
        self.cost_function = cost_function

    def __eq__(self, other):
        return self.is_on_edge(other.node1) and self.is_on_edge(other.node2)

    def __hash__(self):
        return hash(frozenset([self.node1, self.node2]))

    def is_on_edge(self, node):
        return self.node1 == node or self.node2 == node

    def weight(self):
        return self.cost_function(self.node1, self.node2)


class GeometricEdge(Edge):

    def length(self):
        return self.node1.distance_from(geometric_node=self.node2)

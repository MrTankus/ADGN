import math
from collections import defaultdict, deque

from graphs.v1.edges import Edge, GeometricEdge
from graphs.v1.nodes import Node, GeometricNode
from geometry.metrics import euclidean_metric


class Graph(object):

    def __init__(self, nodes=None, edges=None, cost_function=None):
        self.nodes = dict((node.node_id, node) for node in nodes) if nodes else dict()
        self.edges = edges or set()
        self._neighbors = defaultdict(set)
        self._connectivity_components = defaultdict(set)
        self.cost_function = cost_function
        self.original_node_count = len(nodes) if nodes else 0

    def construct_edge(self, node1, node2):
        return Edge(node1=node1, node2=node2, cost_function=self.cost_function)

    def construct_node(self, node_id, data, *args, **kwargs):
        return Node(node_id=node_id, data=data)

    def add_node(self, node_id, data=None, *args, **kwargs):
        new_node = self.construct_node(node_id=node_id, data=data, *args, **kwargs)
        self.nodes[new_node.node_id] = new_node
        return new_node

    def remove_node(self, node):
        edges_to_remove = set(filter(lambda edge: edge.is_on_edge(node=node), self.edges))
        for edge in edges_to_remove:
            self.remove_edge(edge=edge)
        self.nodes.pop(node.node_id)
        self.invalidate_connectivity_component(node=node)

    def get_node(self, node_id):
        return self.nodes[node_id]

    def add_edge(self, node1, node2):
        assert node1.node_id in self.nodes
        assert node2.node_id in self.nodes
        self.edges.add(self.construct_edge(node1=node1, node2=node2))
        self._neighbors[node1.node_id].add(node2)
        self._neighbors[node2.node_id].add(node1)

        self.invalidate_connectivity_component(node=node1)
        self.invalidate_connectivity_component(node=node2)

    def remove_edge(self, edge):
        assert edge in self.edges
        self.edges.remove(edge)
        self._neighbors[edge.node1.node_id].remove(edge.node2)
        self._neighbors[edge.node2.node_id].remove(edge.node1)
        self.invalidate_connectivity_component(node=edge.node1)
        self.invalidate_connectivity_component(node=edge.node2)

    def get_neighbors(self, node):
        assert node.node_id in self.nodes
        if node.node_id in self._neighbors:
            return self._neighbors[node.node_id]
        relevant_edges = filter(lambda edge: edge.is_on_edge(node=node), self.edges)
        for edge in relevant_edges:
            if edge.node1 == node:
                self._neighbors[node.node_id].add(edge.node2)
            else:
                self._neighbors[node.node_id].add(edge.node1)
        return self._neighbors[node.node_id]

    def get_connectivity_components(self):
        visited_nodes = set()
        for node in self.nodes.values():
            if node in visited_nodes:
                continue
            if self._connectivity_components.get(node.node_id):
                continue
            connectivity_component = self.get_connectivity_component(node=node)
            for n in connectivity_component:
                self._connectivity_components[n.node_id] = connectivity_component
            visited_nodes.update(connectivity_component)
        return {self._connectivity_components[node_id] for node_id in self._connectivity_components}

    def get_connectivity_component(self, node):
        if self._connectivity_components.get(node.node_id):
            return self._connectivity_components[node.node_id]
        q = deque([], maxlen=len(self.nodes))
        connectivity_component = set()
        visited_nodes = set()
        q.append(node)
        while len(q) > 0:
            n = q.popleft()
            connectivity_component.add(n)
            visited_nodes.add(n)
            connected_nodes = self.get_neighbors(node=n) - visited_nodes
            q.extend(connected_nodes)
        return frozenset(connectivity_component)

    def get_path(self, source, dest):
        # dijkstra's algorithm
        # 1. Mark all nodes unvisited and store them.
        # 2. Set the distance to zero for our initial node
        # and to infinity for other nodes.
        distances = {vertex: math.inf for vertex in self.nodes.values()}
        previous_vertices = {
            vertex: None for vertex in self.nodes.values()
        }
        distances[source] = 0
        vertices = set(self.nodes.values())

        while vertices:
            # 3. Select the unvisited node with the smallest distance,
            # it's current node now.
            current_vertex = min(
                vertices, key=lambda vertex: distances[vertex])

            # 6. Stop, if the smallest distance
            # among the unvisited nodes is infinity.
            if distances[current_vertex] == math.inf:
                break

            # 4. Find unvisited neighbors for the current node
            # and calculate their distances through the current node.
            # TODO - add cost here!
            for neighbour in self.get_neighbors(current_vertex):
                alternative_route = distances[current_vertex]

                # Compare the newly calculated distance to the assigned
                # and save the smaller one.
                if alternative_route < distances[neighbour]:
                    distances[neighbour] = alternative_route
                    previous_vertices[neighbour] = current_vertex

            # 5. Mark the current node as visited
            # and remove it from the unvisited set.
            vertices.remove(current_vertex)

        path, current_vertex = deque(), dest
        while previous_vertices[current_vertex] is not None:
            path.appendleft(current_vertex)
            current_vertex = previous_vertices[current_vertex]
        if path:
            path.appendleft(current_vertex)
        return path

    def invalidate_connectivity_component(self, node=None):
        if not node:
            self._connectivity_components.clear()
        else:
            cc = self._connectivity_components.get(node.node_id)
            if cc:
                for n in cc:
                    self._connectivity_components.pop(n.node_id, None)

    def validate(self):
        pass


class GeometricGraph(Graph):

    def __init__(self, nodes=None, edges=None, cost_function=None, metric=euclidean_metric):
        super(GeometricGraph, self).__init__(nodes=nodes, edges=edges, cost_function=cost_function)
        self.metric = metric

    def construct_edge(self, node1, node2):
        return GeometricEdge(node1=node1, node2=node2, cost_function=self.cost_function)

    def construct_node(self, node_id, data, *args, **kwargs):
        return GeometricNode(node_id=node_id, data=data, location=kwargs.get('location'), halo=kwargs.get('halo'))

    def get_nearest_neighbors(self, node):
        neighbors = self.get_neighbors(node=node)
        return sorted(neighbors, key=lambda n: self.node_distance(node, n))

    def node_distance(self, n1, n2):
        return self.metric(n1.location, n2.location)

    def get_nearest_node(self, node, from_nodes=None):
        nodes = set(from_nodes) or set(self.nodes.values())
        nodes = nodes - {node}
        return min([(self.node_distance(node, n), n) for n in nodes])[1]

    def get_nodes_in_radius(self, node, radius):
        nodes_in_radius = set()
        for n in self.nodes.values():
            if 0 < self.node_distance(n, node) <= radius:
                nodes_in_radius.add(n)
        return nodes_in_radius

    def find_closest_node_to_connectivity_component(self, connectivity_component):
        nodes_distance = set()
        for cc in self.get_connectivity_components():
            if cc == connectivity_component:
                continue
            nodes_distance.update([(self.node_distance(from_cc_n, cc_n), (from_cc_n, cc_n)) for cc_n in cc for from_cc_n in
                                   connectivity_component])
        info = min(nodes_distance)
        return info[1]

    def geo_distance(self, n1, n2):
        return self.metric(p1=n1.location, p2=n2.location)


class DiskGraph(GeometricGraph):

    def __init__(self, nodes, disk_radius, metric=None):
        super(DiskGraph, self).__init__(nodes=nodes, metric=metric)
        self.disk_radius = disk_radius
        for node_id in self.nodes:
            self.construct_edges(node=self.nodes[node_id])

    def construct_edges(self, node):
        assert node is not None
        if node.node_id in self.nodes:
            existing_edges = set(filter(lambda edge: edge.is_on_edge(node), self.edges))
            edges_to_be_removed = set(filter(lambda edge: self.node_distance(edge.node1, edge.node2) > self.disk_radius,
                                             existing_edges))
            for edge in edges_to_be_removed:
                self.remove_edge(edge=edge)
            existing_edges = existing_edges - edges_to_be_removed
            nodes_in_disk = self.get_nodes_in_radius(node=node, radius=self.disk_radius)
            for n in nodes_in_disk:
                if all([not edge.is_on_edge(n) for edge in existing_edges]):
                    self.add_edge(node1=node, node2=n)

    def add_node(self, node_id, data=None, *args, **kwargs):
        kw = {'halo': self.disk_radius}
        kw.update(kwargs)
        new_node = super(DiskGraph, self).add_node(node_id=node_id, data=data, *args, **kw)
        self.construct_edges(node=new_node)

    def validate(self):
        for edge in self.edges:
            n1 = edge.node1
            n2 = edge.node2
            assert n1.distance_from(n2) <= self.disk_radius


class UDG(DiskGraph):

    def __init__(self, nodes=None):
        super(UDG, self).__init__(nodes=nodes, disk_radius=1, metric=euclidean_metric)

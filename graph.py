import queue
from collections import defaultdict


class Node(object):

    def __init__(self, node_id, data=None):
        self.node_id = node_id
        self.data = data

    def __eq__(self, other):
        return other.node_id == self.node_id

    def __hash__(self):
        return hash(self.node_id)


class GeometricNode(Node):

    def __init__(self, node_id, location, data=None, halo=None):
        super(GeometricNode, self).__init__(node_id=node_id, data=data)
        self.location = location
        self.halo = halo


class Edge(object):

    def __init__(self, node1, node2, cost_function=None):
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


class Graph(object):

    def __init__(self, nodes=None, edges=None):
        self.nodes = dict((node.node_id, node) for node in nodes) if nodes else dict()
        self.edges = edges or set()
        self._neighbors = defaultdict(set)
        self._connectivity_components = defaultdict(set)

    def add_node(self, node):
        self.nodes[node.node_id] = node
        self._connectivity_components.clear()

    def remove_node(self, node):
        edges_to_remove = filter(lambda edge: edge.is_on_edge(node=node), self.edges)
        for edge in edges_to_remove:
            self.remove_edge(edge=edge)
        self.nodes.pop(node.node_id)
        self._connectivity_components.clear()

    def get_node(self, node_id):
        return self.nodes[node_id]

    def add_edge(self, node1, node2):
        assert node1.node_id in self.nodes
        assert node2.node_id in self.nodes
        self.edges.add(Edge(node1=node1, node2=node2))
        self._neighbors[node1.node_id].add(node2)
        self._neighbors[node2.node_id].add(node1)
        self._connectivity_components.clear()

    def remove_edge(self, edge):
        assert edge in self.edges
        self.edges.remove(edge)
        self._neighbors[edge.node1.node_id].remove(edge.node2)
        self._neighbors[edge.node2.node_id].remove(edge.node1)
        self._connectivity_components.clear()

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

    def is_connected(self):
        return len(self.get_connectivity_components()) == 1

    def get_connectivity_components(self):
        if self._connectivity_components:
            return self._connectivity_components
        all_nodes = set(map(lambda item: item[1], self.nodes.items()))
        visited_nodes = set()
        component_index = 0
        for node in all_nodes:
            if node in visited_nodes:
                continue
            q = queue.Queue(maxsize=len(self.nodes))
            q.put(node)
            while q.qsize() > 0:
                n = q.get()
                self._connectivity_components[component_index].add(n)
                visited_nodes.add(n)
                relevant_edges = list(filter(lambda e: e.is_on_edge(node=n), self.edges))
                connected_nodes = set(map(lambda e: e.node1 if e.node1 is not n else e.node2, relevant_edges))
                for connected_node in connected_nodes.difference(visited_nodes):
                    q.put(connected_node)
            component_index += 1
        return self._connectivity_components

    def get_connectivity_componenet(self, node):
        for component_id in self.get_connectivity_components():
            if node in self.get_connectivity_components()[component_id]:
                return component_id
        return None


class GeometricGraph(Graph):

    def __init__(self, nodes=None, edges=None):
        super(GeometricGraph, self).__init__(nodes=nodes, edges=edges)

    def get_nearest_neighbors(self, node):
        neighbors = self.get_neighbors(node=node)
        return sorted(neighbors, key=lambda n: n.location.distance(node.location))

    def get_nearest_node(self, node):
        nearest_node = None
        for node_id in self.nodes:
            n = self.nodes[node_id]
            if n is not node:
                nearest_node = n if nearest_node is None or n.location.distance(node.location) < nearest_node.location.distance(node.location) else nearest_node
        return nearest_node

    def get_nodes_in_radius(self, node, radius):
        nodes_in_radius = set()
        for node_id in self.nodes:
            n = self.nodes[node_id]
            if 0 < n.location.distance(node.location) <= radius:
                nodes_in_radius.add(n)
        return nodes_in_radius


class DiskGraph(GeometricGraph):

    def __init__(self, nodes, disk_radius):
        super(DiskGraph, self).__init__(nodes=nodes)
        self.disk_radius = disk_radius
        for node_id in self.nodes:
            self.construct_edges(node=self.nodes[node_id])

    def construct_edges(self, node):
        assert node is not None
        if node.node_id in self.nodes:
            # Added / Existing Node
            # If node exists - we remove all of its edges and reconstruct them
            existing_edges = list(filter(lambda edge: edge.is_on_edge(node), self.edges))
            for edge in existing_edges:
                self.remove_edge(edge=edge)
            nodes_in_disk = self.get_nodes_in_radius(node=node, radius=self.disk_radius)
            for n in nodes_in_disk:
                self.add_edge(node1=node, node2=n)

    def add_node(self, node):
        super(DiskGraph, self).add_node(node=node)
        self.construct_edges(node=node)


class UDG(DiskGraph):

    def __init__(self, nodes=None):
        super(UDG, self).__init__(nodes=nodes, disk_radius=1)

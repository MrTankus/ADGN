from collections import defaultdict, deque


class Node(object):

    def __init__(self, node_id, data=None):
        self.node_id = node_id
        self.data = data

    def __eq__(self, other):
        return other.node_id == self.node_id

    def __hash__(self):
        return hash(self.node_id)

    def clone(self):
        return Node(node_id=self.node_id, data=self.data)


class GeometricNode(Node):

    def __init__(self, node_id, location, data=None, halo=None):
        super(GeometricNode, self).__init__(node_id=node_id, data=data)
        self.location = location
        self.halo = halo

    def distance_from(self, geometric_node, metric=None):
        if metric and callable(metric):
            return metric(self, geometric_node)
        return self.location.distance(geometric_node.location)

    def clone(self):
        return GeometricNode(node_id=self.node_id, location=self.location.clone(), data=self.data, halo=self.halo)


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


class Graph(object):

    def __init__(self, nodes=None, edges=None):
        self.nodes = dict((node.node_id, node) for node in nodes) if nodes else dict()
        self.edges = edges or set()
        self._neighbors = defaultdict(set)
        self._connectivity_components = defaultdict(set)
        self.original_node_count = len(nodes) if nodes else 0

    def construct_edge(self, node1, node2, cost_function):
        return Edge(node1=node1, node2=node2, cost_function=cost_function)

    def add_node(self, node, *args, **kwargs):
        self.nodes[node.node_id] = node

    def remove_node(self, node):
        edges_to_remove = set(filter(lambda edge: edge.is_on_edge(node=node), self.edges))
        for edge in edges_to_remove:
            self.remove_edge(edge=edge)
        self.nodes.pop(node.node_id)
        self.invalidate_connectivity_component(node=node)

    def get_node(self, node_id):
        return self.nodes[node_id]

    def add_edge(self, node1, node2, cost_function=None):
        assert node1.node_id in self.nodes
        assert node2.node_id in self.nodes
        assert cost_function is None or callable(cost_function)
        self.edges.add(self.construct_edge(node1=node1, node2=node2, cost_function=cost_function))
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

    def is_connected(self):
        return len(self.get_connectivity_components()) == 1

    def get_connectivity_components(self):
        all_nodes = map(lambda item: item[1], self.nodes.items())
        visited_nodes = set()
        for node in all_nodes:
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
            for connected_node in connected_nodes:
                q.append(connected_node)
        return frozenset(connectivity_component)

    def get_all_paths(self, source, destination, path=[]):
        if source.node_id not in self.nodes:
            return []
        path = path + [source]
        if source == destination:
            return [path]
        paths = []
        for node in self.get_neighbors(node=source):
            if node not in path:
                new_paths = self.get_all_paths(source=node, destination=destination, path=path)
                for p in new_paths:
                    paths.append(p)
        return paths

    def get_shortest_path(self, source, destination, path=[]):
        if source.node_id not in self.nodes:
            return None
        path = path + [source]
        if source == destination:
            return path

        shortest = None
        for node in self.get_neighbors(node=source):
            if node not in path:
                new_path = self.get_shortest_path(node, destination, path)
                if new_path:
                    # TODO - take in consideration cost_function
                    if not shortest or len(new_path) < len(shortest):
                        shortest = new_path
        return shortest

    def invalidate_connectivity_component(self, node):
        cc = self._connectivity_components.get(node.node_id)
        if cc:
            for n in cc:
                self._connectivity_components.pop(n.node_id, None)


class GeometricGraph(Graph):

    def __init__(self, nodes=None, edges=None):
        super(GeometricGraph, self).__init__(nodes=nodes, edges=edges)

    def construct_edge(self, node1, node2, cost_function):
        return GeometricEdge(node1=node1, node2=node2, cost_function=cost_function)

    def get_nearest_neighbors(self, node):
        neighbors = self.get_neighbors(node=node)
        return sorted(neighbors, key=lambda n: n.location.distance(node.location))

    def get_nearest_node(self, node):
        nearest_node = None
        for n in self.nodes.values():
            if n is not node:
                nearest_node = n if nearest_node is None or n.location.distance(node.location) < nearest_node.location.distance(node.location) else nearest_node
        return nearest_node

    def get_nodes_in_radius(self, node, radius):
        nodes_in_radius = set()
        for n in self.nodes.values():
            if 0 < n.distance_from(node) <= radius:
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
            existing_edges = set(filter(lambda edge: edge.is_on_edge(node), self.edges))
            edges_to_be_removed = set(filter(lambda edge: edge.length() > self.disk_radius, existing_edges))
            for edge in edges_to_be_removed:
                self.remove_edge(edge=edge)
            existing_edges = existing_edges - edges_to_be_removed
            nodes_in_disk = self.get_nodes_in_radius(node=node, radius=self.disk_radius)
            for n in nodes_in_disk:
                if all([not edge.is_on_edge(n) for edge in existing_edges]):
                    self.add_edge(node1=node, node2=n)

    def add_node(self, node, *args, **kwargs):
        super(DiskGraph, self).add_node(node=node, *args, **kwargs)
        self.construct_edges(node=node)


class UDG(DiskGraph):

    def __init__(self, nodes=None):
        super(UDG, self).__init__(nodes=nodes, disk_radius=1)

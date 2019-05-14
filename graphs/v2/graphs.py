import itertools
from collections import deque, defaultdict

import numpy as np
from scipy.sparse import coo_matrix
from geometry.metrics import euclidean_metric


class Vertex(object):

    def __init__(self, vertex_id, **kwargs):
        self.id = vertex_id
        self.metadata = kwargs or dict()

    def get(self, key, default=None):
        return self.metadata.get(key, default)

    def set(self, key, data):
        self.metadata[key] = data

    def clone(self):
        return Vertex(self.id, **self.metadata)

    def __eq__(self, other):
        return type(self) == type(other) and self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __repr__(self):
        return "Vertex [id: " + str(self.id) + "]"


class Edge(object):

    def __init__(self, v1, v2, weight=1, directed=False):
        self.v1 = v1
        self.v2 = v2
        self.directed = directed
        self.weight = weight

    def __eq__(self, other):
        if self.directed:
            if not other.directed:
                return False
            return self.v1 == other.v1 and self.v2 == other.v2
        else:
            if other.directed:
                return False
            return (self.v1 == other.v1 and self.v2 == other.v2) or (self.v1 == other.v2 and self.v2 == other.v2)

    def __hash__(self):
        if self.directed:
            return hash((self.v1, self.v2))
        else:
            return hash(frozenset([self.v1, self.v2]))


class Graph(object):

    def __init__(self, vertices=None, edges=None, directed=False):
        """
        :param vertices: a set of Vertex objects
        :param edges: a set of Edge object
        :param directed: if set to True - all edges will be set to directed edges from edge.v1 to edge.v2
        """
        self.vertices = vertices or set()
        self.edges = edges or set()
        self.directed = directed

        self.is_sparse = ((len(self.vertices) * (len(self.vertices) - 1) / 2) - len(self.edges)) / len(self.vertices) > 0.5 if self.vertices else False

        self.vertices_indices_map = dict(zip(self.vertices, range(len(self.vertices))))
        self.adj = self.get_adjacency_matrix()

        self.paths = dict()
        self.connectivity_components_map = dict()
        self.connectivity_components = set()

    def add_vertex(self, vertex):
        size = len(self.vertices)
        self.adj = np.insert(self.adj, size, 0, axis=0)
        self.adj = np.insert(self.adj, size, 0, axis=1)
        self.vertices.add(vertex)
        self.vertices_indices_map[vertex] = size

    def add_edge(self, v1, v2, weight=1):
        v1_index = self.vertices_indices_map.get(v1)
        v2_index = self.vertices_indices_map.get(v2)
        if not self.directed:
            self.adj[v2_index, v1_index] = weight
        self.adj[v1_index, v2_index] = weight
        self.edges.add(Edge(v1=v1, v2=v2, weight=weight, directed=self.directed))
        self.paths.clear()
        self.connectivity_components_map.clear()
        self.connectivity_components.clear()

    def remove_edge(self, edge):
        v1_index = self.vertices_indices_map.get(edge.v1)
        v2_index = self.vertices_indices_map.get(edge.v2)
        if not self.directed:
            self.adj[v2_index, v1_index] = 0
        self.adj[v1_index, v2_index] = 0
        self.edges.remove(edge)
        self.paths.clear()
        self.connectivity_components_map.clear()
        self.connectivity_components.clear()

    def get_adjacency_matrix(self):
        # TODO - implement for sparse matrix
        # if self.is_sparse:
        #     adj = coo_matrix((len(self.vertices), len(self.vertices)), dtype=np.float)
        # else:
        adj = np.zeros(shape=(len(self.vertices), len(self.vertices)), dtype=np.float)
        for edge in self.edges:
            if not self.directed:
                adj[self.vertices_indices_map.get(edge.v2), self.vertices_indices_map.get(edge.v1)] = edge.weight
            adj[self.vertices_indices_map.get(edge.v1), self.vertices_indices_map.get(edge.v2)] = edge.weight
        return adj

    def calculate_paths(self):
        paths = dict()
        path = np.eye(N=len(self.vertices))
        for n in range(len(self.vertices)):
            paths[n + 1] = path @ self.adj
            path = paths[n + 1]
        return paths

    def get_neighbors(self, vertex):
        neighbors = set()
        reverse_vertex_index_mapping = dict(map(reversed, self.vertices_indices_map.items()))
        vertex_index = self.vertices_indices_map.get(vertex)
        for index in np.where(self.adj[vertex_index] != 0)[0]:
            neighbors.add(reverse_vertex_index_mapping.get(index))
        return neighbors

    def get_path_length(self, v1, v2):
        if len(self.paths) == 0:
            self.paths = self.calculate_paths()
        for n in self.paths:
            v1_index = self.vertices_indices_map[v1]
            v2_index = self.vertices_indices_map[v2]
            if self.paths[n][v1_index, v2_index] != 0 or self.paths[n][v2_index, v1_index] != 0:
                return n
        return np.inf

    def get_connectivity_components(self):
        if self.connectivity_components:
            return self.connectivity_components
        self.connectivity_components_map = dict()
        for vertex in self.vertices:
            if vertex.id in self.connectivity_components_map:
                continue
            cc = self.get_connectivity_component(vertex=vertex)
            self.connectivity_components.add(cc)
            for v in cc:
                self.connectivity_components_map[v.id] = cc
        return self.connectivity_components

    def get_connectivity_component(self, vertex):
        if vertex.id in self.connectivity_components_map:
            return self.connectivity_components_map[vertex.v.id]
        q = deque([], maxlen=len(self.vertices))
        connectivity_component = set()
        visited_vertices = set()
        q.append(vertex)
        while len(q) > 0:
            v = q.popleft()
            connectivity_component.add(v)
            visited_vertices.add(v)
            connected_vertices = self.get_neighbors(vertex=v) - visited_vertices
            q.extend(connected_vertices)
        return frozenset(connectivity_component)


class DiskGraph(Graph):

    def __init__(self,  vertices, radius, metric=euclidean_metric, directed=False):
        self.radius = radius
        self.metric = metric
        edges = set()
        if vertices:
            pairs = itertools.combinations(vertices, 2)
            for v1, v2 in pairs:
                if self.metric(v1.get('location'), v2.get('location')) <= self.radius:
                    edges.add(Edge(v1=v1, v2=v2, weight=1))
        super(DiskGraph, self).__init__(vertices=vertices, edges=edges, directed=directed)

    def add_vertex(self, vertex):
        vertex.set('halo', self.radius)
        super(DiskGraph, self).add_vertex(vertex=vertex)
        near_vertices = filter(lambda v: 0 < self.metric(p1=v.get('location'), p2=vertex.get('location')) <= self.radius, self.vertices)
        for v in near_vertices:
            self.add_edge(v, vertex)

    def add_edge(self, v1, v2, weight=1):
        if self.metric(p1=v1.get('location'), p2=v2.get('location')) <= self.radius:
            super(DiskGraph, self).add_edge(v1=v1, v2=v2, weight=weight)

    def construct_edges(self, vertex):
        existing_edges = filter(lambda e: e.v1 == vertex or e.v2 == vertex, self.edges)
        near_vertices = filter(lambda v: 0 < self.metric(p1=v.get('location'), p2=vertex.get('location')) <= self.radius, self.vertices)
        index = self.vertices_indices_map[vertex]
        self.adj[index, :] = 0
        self.adj[:, index] = 0
        edges_to_be_removed = set(filter(lambda edge: self.metric(edge.v1.get('location'), edge.v2.get('location')) > self.radius, existing_edges))

        for edge in edges_to_be_removed:
            super(DiskGraph, self).remove_edge(edge)

        for v in near_vertices:
            super(DiskGraph, self).add_edge(v1=v, v2=vertex)


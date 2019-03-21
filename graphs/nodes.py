
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

    def get(self, key):
        if self.data:
            return self.data.get(key, None)
        return None


class GeometricNode(Node):

    def __init__(self, node_id, location, data=None, halo=None):
        super(GeometricNode, self).__init__(node_id=node_id, data=data)
        self.location = location
        self.halo = halo

    def clone(self):
        return GeometricNode(node_id=self.node_id, location=tuple(self.location), data=self.data, halo=self.halo)

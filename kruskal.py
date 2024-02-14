class DisjointSet:
    def __init__(self, vertices):
        self.parent = {v: v for v in vertices}

    def find(self, vertex):
        if self.parent[vertex] != vertex:
            self.parent[vertex] = self.find(self.parent[vertex])
        return self.parent[vertex]

    def union(self, u, v):
        self.parent[self.find(u)] = self.find(v)


def kruskal(graph):
    vertices = {v for edge in graph for v in edge[:2]}  # Extracting unique vertices from edges
    res = []
    disjoint_set = DisjointSet(vertices)
    edges = sorted(graph, key=lambda x: x[2]['weight'])  # sort edges by weight

    for u, v, data in edges:
        if disjoint_set.find(u) != disjoint_set.find(v):
            res.append((u, v, {'weight': data['weight']}))
            disjoint_set.union(u, v)

    return res



graph = [
    (0, 1, {'weight': 1}), (1, 2, {'weight': 2}), (2, 3, {'weight': 9}),
    (3, 4, {'weight': 8}), (2, 4, {'weight': 7}), (4, 5, {'weight': 5}),
    (5, 6, {'weight': 3}), (6, 0, {'weight': 4}), (0, 5, {'weight': 8}),
    (1, 6, {'weight': 3}), (1, 5, {'weight': 2}), (2, 5, {'weight': 6})
]

print(kruskal(graph))

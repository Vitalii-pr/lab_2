'''Bellman Ford'''

def bellman_ford(lst_edg_wei: list) -> None:
    '''
    Bellman Ford algorithm for finding the shortest distance between vertices

    >>> bellman_ford([(0, 2, {'weight': 2}), (0, 3, {'weight': 13}), (0, 5, {'weight': 10}), \
(0, 6, {'weight': -1}), (0, 7, {'weight': 4}), (0, 8, {'weight': 14}), (1, 3, {'weight': 11}), \
(1, 4, {'weight': 9}), (1, 6, {'weight': 4}), (1, 7, {'weight': 2}), (1, 8, {'weight': 0}), \
(2, 5, {'weight': 17}), (2, 6, {'weight': -1}), (2, 7, {'weight': -5}), (2, 8, {'weight': 19}), \
(3, 0, {'weight': -2}), (3, 4, {'weight': 14}), (3, 6, {'weight': 15}), (3, 7, {'weight': 11}), \
(3, 9, {'weight': 3}), (4, 2, {'weight': 11}), (4, 6, {'weight': 11}), (4, 8, {'weight': 6}), \
(5, 7, {'weight': 17}), (5, 8, {'weight': 14}), (5, 9, {'weight': -5}), (6, 4, {'weight': 6}), \
(6, 7, {'weight': 4}), (6, 8, {'weight': 11}), (7, 8, {'weight': 11}), (7, 9, {'weight': -3}), \
(8, 7, {'weight': 6}), (8, 9, {'weight': -3})])
    ({0: 0, 2: 2, 3: 13, 4: 5, 5: 10, 6: -1, 7: -3, 8: 8, 9: -6}, {0: [], 2: [0], 3: [0], \
4: [6], 5: [0], 6: [0], 7: [2], 8: [7], 9: [7]})
    '''
    lst = list(map(lambda x: (x[0], x[1], x[2]['weight']), lst_edg_wei))
    unique_vertices = set(list(map(lambda x: x[0], lst)) + list(map(lambda x: x[1], lst)))
    shortest_distance, predecessor = initialize_source(unique_vertices)
    for _ in range(len(lst) - 1):
        for v1, v2, w in lst:
            shortest_distance, predecessor = relax(v1, v2, w, shortest_distance, predecessor)
    for vertice1, vertice2, weight in lst:
        if shortest_distance[vertice2] > shortest_distance[vertice1] + weight:
            return "Negative cycle detected"

    new_dist = {vert:weight for vert, weight in shortest_distance.items() if weight != float('inf')}
    new_pred = {vert:old_lst for vert, old_lst in predecessor.items() if vert == 0 or old_lst != []}
    return new_dist, new_pred

def relax(v1, v2, weight, d, p):
    '''
    Relaxes given edge and updates distance dictionary
    and predecessor dictionary.
    '''
    if d[v2] > d[v1] + weight:
        d[v2] = d[v1] + weight
        p[v2] = [v1]
    return d, p

def initialize_source(vertices, start_v=0):
    '''
    Creates shortest_distance with inf edges for later updates
    and creates predecessor dictionary for later new previous vertices
    '''
    shortest_distance = {}
    predecessor = {}
    for v in vertices:
        shortest_distance[v] = float('inf')
        predecessor[v] = []
    shortest_distance[start_v] = 0
    return shortest_distance, predecessor

'''Bellman Ford'''

def bellman_ford(lst_edg_wei: list) -> None:
    '''
    Bellman Ford algorithm for finding the shortest distance between vertices
    '''
    lst = list(map(lambda x: (x[0], x[1], x[2]['weight']), list(lst_edg_wei.edges(data=True))))
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

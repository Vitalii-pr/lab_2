INF = float('inf')

def adjacency_matrix(graph):
    num_of_nodes = len(graph.nodes())

    adj_matrix = [[INF] * num_of_nodes for _ in range(num_of_nodes)]

    for u, v, w in graph.edges(data=True):
        adj_matrix[u][v] = w.get('weight')
        if not graph.is_directed():
            adj_matrix[v][u] = w.get('weight')

    for i in range(num_of_nodes):
        adj_matrix[i][i] = 0

    return adj_matrix

def floyd_warshall(graph):
    res = dict()
    adj_matrix = adjacency_matrix(graph)
    num_of_nodes = len(adj_matrix)

    for k in range(num_of_nodes):
        for i in range(num_of_nodes):
            for j in range(num_of_nodes):
                adj_matrix[i][j] = min(adj_matrix[i][j], adj_matrix[i][k] + adj_matrix[k][j])

    for i in range(len(adj_matrix)):
        res[f'Distance with {i} source'] = {j:adj_matrix[i][j] for j in range(len(adj_matrix[i]))}

    return res

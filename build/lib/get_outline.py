import networkx as nx
import numpy as np

def get_neighbors(q, r, s):
    return [
        (q,r+1,s-1),
        (q+1,r,s-1),
        (q+1,r-1,s),
        (q,r-1,s+1),
        (q-1,r,s+1),
        (q-1,r+1,s),
    ]

def get_direction(v, w):
    return (v[0] - w[0], v[1] - w[1], v[2] - w[2])

def simplify_outline(outline):
    prev_dir = None
    prev = None
    nodes = []
    for node in outline:
        change_dir = False
        if prev is not None:
            dir = get_direction(prev, node)
            if prev_dir == dir:
                nodes.pop()
            prev_dir = dir
        prev = node
        nodes.append(node)
    return nodes

def iter_edges(node, nodes):
    neighbors = [
        neighbor if neighbor in nodes else None
        for neighbor in get_neighbors(*node)
    ]
    # completly surrounded, so no outside edges
    if None not in neighbors:
        return []
    i = neighbors.index(None)
    start = None
    end = None
    for i in range(i+1, i+6):
        i = i % 6
        
        # End of group
        if neighbors[i] is None:
            if end:
                yield (node, start)
                yield (node, end)
            start = None
            end = None
        
        # Start of group
        elif start is None:
            start = neighbors[i]

        # Continuation of group
        else:
            end = neighbors[i]

    if end:
        yield (node, start)
        yield (node, end)

def get_outline(nodes):
    nodes = {tuple(node) for node in nodes}
    
    # Add all edges between nodes
    G = nx.Graph()
    for node in nodes:
        G.add_edges_from(iter_edges(node, nodes))

    if len(G.edges) == 0:
        return None
    outline = max(nx.simple_cycles(G), key=len)
    outline = simplify_outline(outline)
    return np.array([np.array(node) for node in outline])
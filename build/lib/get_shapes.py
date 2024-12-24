import numpy as np
from lib.get_outline import get_outline

# https://github.com/marcharper/python-ternary/blob/master/ternary/helpers.py
def simplex_iterator(scale, boundary=True):
    """
    Systematically iterates through a lattice of points on the 2-simplex.

    Parameters
    ----------
    scale: Int
        The normalized scale of the simplex, i.e. N such that points (x,y,z)
        satisify x + y + z == N

    boundary: bool, True
        Include the boundary points (tuples where at least one
        coordinate is zero)

    Yields
    ------
    3-tuples, There are binom(n+2, 2) points (the triangular
    number for scale + 1, less 3*(scale+1) if boundary=False
    """

    start = 0
    if not boundary:
        start = 1
    for i in range(start, scale + (1 - start)):
        for j in range(start, scale + (1 - start) - i):
            k = scale - i - j
            yield np.array([i, j, k])

def groupby(iter, grouper):
    g = {}
    for val in iter:
        g.setdefault(grouper(val),[]).append(val)
    return g.items()

def get_shapes(scores, density):

    def best_for_coord(idx):
        return (scores * (idx / density)).sum(axis=1).argmin()

    shapes = {}
    for id, points in groupby(simplex_iterator(density), best_for_coord):
        if len(points) < 3:
            continue
        outline = get_outline(points)
        if outline is None:
            continue
        shapes[id] = outline
    return shapes
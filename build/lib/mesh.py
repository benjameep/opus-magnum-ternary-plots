from __future__ import annotations
import typing as t
import numpy as np
from collections import namedtuple, defaultdict
from scipy.spatial import ConvexHull

SCORES = np.array([[]])

def best_for_coord(idx):
    idx = np.append(idx, 1 - idx.sum())
    return (SCORES * idx).sum(axis=1).argmin()

class Corner(t.NamedTuple):
    p: np.ndarray
    cat: int

class SidePoint(t.NamedTuple):
    p: np.ndarray
    c1: int
    c2: int

class Side(t.NamedTuple):
    p1: Corner
    p2: Corner
    cats: t.List[int]
    points: np.ndarray

class Triangle(t.NamedTuple):
    s1: Side
    s2: Side
    s3: Side

class TrianglePoint(t.NamedTuple):
    p: np.ndarray
    cats: t.List[int]

def get_corner(x, y=None) -> Corner:
    if isinstance(x, np.ndarray):
        assert x.dtype == np.dtype('float32'), x.dtype
        assert x.shape == (2,), x.shape
        p = x
    else:
        p = np.array([x,y], dtype='float32')
    return Corner(p=p, cat=best_for_coord(p))

def iter_points(p1: Corner, p2: Corner, depth: int) -> t.Iterable[SidePoint]:
    if p1.cat == p2.cat:
        return

    m = (p1.p + p2.p) / 2
    if depth == 0:
        yield SidePoint(p=m, c1=p1.cat, c2=p2.cat)
        return

    midpoint = get_corner(m)
    if p1.cat != midpoint.cat:
        yield from iter_points(p1, midpoint, depth-1)
    if midpoint.cat != p2.cat:
        yield from iter_points(midpoint, p2, depth-1)

def get_side(p1: Corner, p2: Corner, depth: int) -> Side:
    cats = [p1.cat]
    points = []
    for p in iter_points(p1, p2, depth):
        cats.append(p.c2)
        points.append(p.p)
    assert cats[-1] == p2.cat
    return Side(p1, p2, cats, points=np.array(points))

def get_distances(points: np.ndarray, ref: np.ndarray, axis=0) -> np.ndarray:
    return np.sqrt(np.sum((points - ref)**2, axis=axis))

def get_split_idx(side: Side) -> int:
    if len(side.points) == 0:
        return 0
    distances_from_p1 = get_distances(side.points, side.p1.p, axis=1)
    total_dist = get_distances(side.p2.p, side.p1.p)
    greater_than_half = (distances_from_p1 / total_dist) >= 0.5
    if True not in greater_than_half:
        return len(greater_than_half)
    return greater_than_half.argmax()

def split_side(side: Side) -> t.Tuple[Side, Side]:
    idx = get_split_idx(side)
    midpoint = Corner((side.p1.p + side.p2.p) / 2, cat=side.cats[idx])
    s1 = Side(side.p1, midpoint, side.cats[:idx] + [midpoint.cat], points=side.points[:idx])
    s2 = Side(midpoint, side.p2, side.cats[idx:], points=side.points[idx:])
    return s1, s2

def reverse_side(side: Side) -> Side:
    return Side(
        p1=side.p2,
        p2=side.p1,
        cats=side.cats[::-1],
        points=side.points[::-1],
    )

def get_sub_triangles(triangle: Triangle, depth: int) -> t.List[Triangle]:
    p1_m1, m1_p2 = split_side(triangle.s1)
    p2_m2, m2_p3 = split_side(triangle.s2)
    p3_m3, m3_p1 = split_side(triangle.s3)
    m1, m2, m3 = (m1_p2.p1, m2_p3.p1, m3_p1.p1)
    m1_m2 = get_side(m1, m2, depth)
    m2_m3 = get_side(m2, m3, depth)
    m3_m1 = get_side(m3, m1, depth)
    
    return [
        Triangle(p1_m1, reverse_side(m3_m1), m3_p1),
        Triangle(p2_m2, reverse_side(m1_m2), m1_p2),
        Triangle(p3_m3, reverse_side(m2_m3), m2_p3),
        Triangle(m1_m2, m2_m3, m3_m1),
    ]

def contains_intersection(triangle: Triangle) -> bool:
    counts = defaultdict(int)
    sides = set()
    corners = set()
    for side in triangle:
        counts[side.p1.cat] += 1
        corners.add(side.p1.cat)
        for c in side.cats[1:-1]:
            counts[c] += 1
            sides.add(c)
    triple_side = False
    for cat in sides:
        if counts[cat] == 1:
            return True
        if counts[cat] == 3:
            triple_side = True
        if cat in corners:
            corners.remove(cat)
    return not triple_side and (len(corners) == 3)

def get_triangle_point(triangle: Triangle) -> TrianglePoint:
    return TrianglePoint(
        p = (triangle.s1.p1.p + triangle.s2.p1.p + triangle.s3.p1.p) / 3,
        cats=list({
            *triangle.s1.cats,
            *triangle.s2.cats,
            *triangle.s3.cats,
        })
    )

def iter_intersections(triangle, depth):
    if not contains_intersection(triangle):
        return
    if depth == 0:
        yield get_triangle_point(triangle)
        return
    for sub_triangle in get_sub_triangles(triangle, depth-1):
        yield from iter_intersections(sub_triangle, depth-1)

def construct_triangle(p1, p2, p3, depth):
    corners = [get_corner(x,y) for x,y in [p1,p2,p3]]
    return Triangle(
        get_side(corners[0], corners[1], depth),
        get_side(corners[1], corners[2], depth),
        get_side(corners[2], corners[0], depth),
    )
    
def get_polygons(scores, depth):
    global SCORES
    SCORES = scores
    root = construct_triangle((0.0,0.0),(0.0,1.0),(1.0,0.0), depth)

    cat_points = defaultdict(list)    
    for side in root:
        cat_points[side.p1.cat].append(side.p1.p)
        for i,point in enumerate(side.points):
            cat_points[side.cats[i]].append(point)
            cat_points[side.cats[i+1]].append(point)
    
    for intersection in iter_intersections(root, depth):
        for cat in intersection.cats:
            cat_points[cat].append(intersection.p)
    
    polygons = {}
    for id, points in cat_points.items():
        if len(points) < 3:
            continue
        try:
            hull = ConvexHull(np.array(points))
        except:
            continue
        polygons[id] = np.array([
            hull.points[i] for i in hull.vertices
        ])
    
    return polygons
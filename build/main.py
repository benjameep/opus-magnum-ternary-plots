import lib.api as api
from lib.mesh import get_polygons
import numpy as np
import time
from pathlib import Path
import json
from tqdm import tqdm

EXPORT_DIR = Path(__file__).parent.parent / 'data'
assert EXPORT_DIR.exists()

def get_frontier(df, metrics=['cost','cycles','area'], include_overlap=False):
    def is_frontier(row):
        better = df.gif != row.gif
        for metric in metrics:
            better &= df[metric] <= row[metric]
        return ~better.any()

    if not include_overlap:
        df = df.query('~overlap')
    
    df = df.drop_duplicates(subset=metrics)
    return df[df.apply(is_frontier, axis=1)].reset_index(drop=True)

def linear_norm(s):
        return (s - s.min()) / (s.max() - s.min())

SQRT3OVER2 = np.sqrt(3) / 2
def to_yx_percent(shape):
    shape = shape * 100
    return np.array([
        shape[:,1] * SQRT3OVER2,
        shape[:,0] + shape[:,1] / 2,
    ]).T

import struct
import base64
def pack_points(points):
    points = points.flatten()
    return base64.b64encode(struct.pack(f'<{len(points)}f', *points)).decode()

def process_solutions(
            puzzle_id,
            metrics=['area','cycles','cost'],
            include_overlap=False,
            depth=24
        ):
    df = api.get_solutions(puzzle_id)
    df = get_frontier(df, metrics, include_overlap)
    scores = df[metrics].apply(linear_norm).to_numpy()
    # print(json.dumps(scores.tolist()))
    shapes = get_polygons(scores, depth)
    solutions = []
    for id, shape in shapes.items():
        row = df.iloc[id].to_dict()
        solutions.append({
            'gif': row['gif'],
            'categories': row['categories'],
            'metrics': {
                metric: row[metric]
                for metric in metrics
            },
            'color': int(id) % 6,
            'shape': pack_points(to_yx_percent(shape)),
        })
    return solutions

def process_all_puzzles(metrics=['area','cycles','cost'], include_overlap=False, depth=24):
    now = time.time() * 1000
    puzzles = api.list_puzzles()
    
    json.dump(puzzles, (EXPORT_DIR / 'puzzles.json').open('w'))

    for puzzle in tqdm(puzzles):
        filepath = (EXPORT_DIR / f'solutions/{puzzle["id"]}.json')
        data = {
            'id': puzzle['id'],
            'name': puzzle['name'],
            'collection': puzzle['collection'],
            'group': puzzle['group'],
            'last_updated': now,
            'solutions': process_solutions(
                puzzle['id'],
                metrics=metrics,
                include_overlap=include_overlap,
                depth=depth
            ),
            'metrics': metrics,
            'include_overlap': include_overlap,
        }
        json.dump(data, filepath.open('w'))

if __name__ == '__main__':    
    process_all_puzzles(
        metrics=['area','cycles','cost'],
        include_overlap=False,
        depth=24
    )
    
    # process_solutions('P020', metrics=['area','cycles','cost'])
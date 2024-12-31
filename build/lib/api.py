import requests
import pandas as pd
import numpy as np

BASE_URL = 'https://zlbb.faendir.com/om'

def list_puzzles():
    r = requests.get(BASE_URL + '/puzzles')
    r.raise_for_status()
    assert r.headers['Content-Type'] == 'application/json'
    return pd.json_normalize(r.json()).rename(columns={
        'displayName': 'name',
        'group.displayName': 'group',
        'group.collection.displayName': 'collection',
    })[['id','name','collection','group']].to_dict(orient='records')

def list_puzzles_with_new_records(since):
    r = requests.get(BASE_URL + '/records/new/' + since)
    r.raise_for_status()
    assert r.headers['Content-Type'] == 'application/json'
    new_puzzles = {}
    for r in r.json():
        puzzle = r['puzzle']
        new_puzzles[puzzle['id']] = {
            'id': puzzle['id'],
            'name': puzzle['displayName'],
            'collection': puzzle['group']['collection']['displayName'],
            'group': puzzle['group']['displayName'],
        }
    return list(new_puzzles.values())

def get_solutions(puzzle_id):
    r = requests.get(BASE_URL + f'/puzzle/{puzzle_id}/records', params={
        'includeFrontier': True
    })
    r.raise_for_status()
    assert r.headers['Content-Type'] == 'application/json'
    raw = pd.DataFrame(r.json())
    df = pd.concat([
        raw[['gif','categoryIds','lastModified']].rename(columns={'categoryIds': 'categories','lastModified': 'last_modified'}),
        pd.DataFrame(raw.score.tolist()),
    ], axis=1)
    df['last_modified'] = pd.to_datetime(df['last_modified']).astype(np.int64) / int(1e6)
    return df
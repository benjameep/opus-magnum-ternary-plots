import requests
import pandas as pd

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

def get_solutions(puzzle_id):
    r = requests.get(BASE_URL + f'/puzzle/{puzzle_id}/records', params={
        'includeFrontier': True
    })
    r.raise_for_status()
    assert r.headers['Content-Type'] == 'application/json'
    raw = pd.DataFrame(r.json())
    return pd.concat([
        raw[['gif','categoryIds']].rename(columns={'categoryIds': 'categories'}),
        pd.DataFrame(raw.score.tolist()),
    ], axis=1)
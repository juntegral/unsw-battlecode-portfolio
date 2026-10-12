#!/usr/bin/env python3
"""Check unchanged old rows and compare ported counts with the original ladder scan."""
import sys
sys.dont_write_bytecode = True
import ast
import json
from pathlib import Path
from types import SimpleNamespace
from collections import Counter, deque, defaultdict
import replay_format
from count_local import scan, edge_id
from ram_defs import measures, fails, H, swing, RAM_FIELDS, TARGETS, REACHES, VIEWS

HERE = Path(__file__).resolve().parent
WORK = HERE.parent/'work'


def oracle(path, row):
    tree = ast.parse((WORK/'at_scan.py').read_text())
    defs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and getattr(n, 'name', '') != 'main']
    src = ast.parse((HERE.parents[4]/'tools/ladder_replay.py').read_text())
    defs += [n for n in src.body if isinstance(n, ast.FunctionDef) and n.name == 'canonical_edges']
    ns = dict(replay=SimpleNamespace(load=lambda _: replay_format.load(path), point=replay_format.point),
              Path=Path, defaultdict=defaultdict, deque=deque, Counter=Counter,
              STEP=((0,-1),(1,0),(0,1),(-1,0)), CAP=8, edge_id=edge_id)
    exec(compile(ast.Module(body=defs, type_ignores=[]), 'at_scan oracle', 'exec'), ns)
    dummy = dict(battle=0, game=0, map_key=row['map'], our_side='AB'[row['side']],
                 opponent_rating=0, result=row['result'], ended_by=row['how'], queens_at_end=[])
    return ns['scan'](dummy, {})


def main():
    baseline = HERE/'rams-before.jsonl'
    before = [json.loads(x) for x in baseline.read_text().splitlines()] if baseline.exists() else []
    rows = [json.loads(x) for x in (HERE/'rows.jsonl').read_text().splitlines()]
    required = set(RAM_FIELDS) | {'alive_r200', 'alive_r300', 'longest_r300', 'longest_end'}
    required.update(f'ram_{t}_{reach}_{view}_{f}' for t in TARGETS for reach in REACHES
                    for view in VIEWS for f in ('chances', 'taken'))
    for row in rows:
        for side in ('ours', 'theirs'):
            assert required <= row['measures'][side].keys(), (row['replay'], side, 'missing fields')
    by = {r['replay']:r for r in rows}
    for old in before:
        new = by[old['replay']]
        for f, value in old.items():
            if f == '_signature':
                continue
            if f == 'measures':
                for s in value:
                    for k, v in value[s].items():
                        assert new[f][s][k] == v, (old['replay'], s, k)
            else:
                assert new[f] == value, (old['replay'], f)
    source = ast.parse((WORK/'at_more.py').read_text())
    ns = {}
    exec(compile(ast.Module(body=[n for n in source.body if isinstance(n, ast.FunctionDef) and n.name in ('fails','H','swing')], type_ignores=[]), 'at_more oracle', 'exec'), ns)
    for fn in (fails, H, swing):
        import inspect
        actual = ast.parse(inspect.getsource(fn)).body[0]
        original = next(n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == fn.__name__)
        assert [ast.dump(n) for n in actual.body] == [ast.dump(n) for n in original.body]
    selected = []
    for predicate in (lambda r:r['side']==0 and r['map']=='sqheld_portalrooms_large_90003',
                      lambda r:r['side']==1 and r['map'].startswith('ladder_stripes'),
                      lambda r:r['side']==0 and r['width']*r['height']>1200,
                      lambda r:r['side']==1 and r['map']=='sqheld_portalrooms_small_90021'):
        selected.append(next(r for r in rows if predicate(r)))
    for row in selected:
        g = oracle(Path(row['replay']), row)
        chs = [r for r in g['chs'] if not r[4] and 2 <= r[3] <= 4]
        hos = g['hos']
        for r in chs:
            r[1] = ('ours', 'theirs')[r[1]]
        for x in hos:
            x['ms'] = ('ours', 'theirs')[x['ms']]
        q300 = bool(g['series'].get(300, [0,0,0,0])[3])
        for s in ('ours','theirs'):
            expected = measures(chs, hos, s, g['cells'], q300)
            assert all(row['measures'][s][k] == v for k,v in expected.items()), row['replay']
        for want, got in zip(hos, row['ram_meetings']):
            assert all(got[k] == want[k] for k in got), (row['replay'], want, got)
        assert len(hos) == len(row['ram_meetings'])
        for r in chs:
            gg = dict(feed=300 if g['cells']>600 and q300 else 400, aggr=g['cells']<=1200)
            assert fails(gg,r) == ns['fails'](gg,r,True)
            assert H(gg,r) == ns['H'](gg,r)
        print('oracle OK:', row['arm'], row['map'], row['side'], len(chs), 'chances;', len(hos), 'meetings', flush=True)
    print(f'PASS: {len(before)} old rows unchanged; {len(rows)} recounted rows; {len(selected)} original-scan comparisons')


if __name__ == '__main__':
    main()

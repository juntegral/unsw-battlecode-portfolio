#!/usr/bin/env python3
"""Row-by-row comparison of the earlier count (deaths/rows.json) with this recount (verify/deaths.json).
Run from the repo root after recount.py:  python3 data/local/hunter38/verify/compare.py
For every wall / own-body death the earlier script called "had a safe move", it prints that move and what the tile
held at the start of her fatal action according to this recount."""
import sys
sys.dont_write_bytecode = True
import json, os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
old = json.load(open(os.path.join(os.path.dirname(HERE), 'deaths', 'rows.json')))
new = json.load(open(os.path.join(HERE, 'deaths.json')))
rows = old['deaths'] if isinstance(old, dict) and 'deaths' in old else old
print('earlier file: type', type(old).__name__, 'keys', list(old)[:8] if isinstance(old, dict) else len(old))
print('earlier row keys:', sorted(rows[0].keys()))
mine = {(d['run'], d['file'], d['rnd']): d for d in new if d['who'] == 'our'}


def key(r):
    run = {'normal': 'plain'}.get(r.get('dataset'), r.get('dataset'))
    name = os.path.basename(r.get('replay') or '').replace('.replay', '')
    return run, name, r.get('round', r.get('rnd'))


miss = [key(r) for r in rows if key(r) not in mine]
print('earlier rows', len(rows), 'mine', len(mine), 'earlier rows with no match in mine', len(miss), miss[:3])
print('cause agrees', sum(r['cause'] == mine[key(r)]['cause'] for r in rows if key(r) in mine))
tally = Counter()
for r in rows:
    k = key(r)
    if k not in mine or r['cause'] not in ('wall', 'self', 'body'):
        continue
    m = mine[k]
    cls = r['classification']
    tally[(k[0], r['cause'], cls, 'forced here' if m['forced'] else 'not forced here')] += 1
    if cls != 'forced':
        opt = m['last']['opt'] or {}
        said = r.get('safe_moves') or r.get('legal_moves')
        print(f"{k[0]:6} {k[1]:38} r{k[2]:3} {r['cause']:4} earlier={cls!r} safe={r.get('safe_moves')} legal={r.get('legal_moves')} "
              f"| here: len={m['len']} those tiles hold {[opt.get(d) for d in (said or [])]} all={''.join(opt.get(d, '?')[0] for d in 'NESW')}")
print()
for k, v in sorted(tally.items()):
    print(k, v)

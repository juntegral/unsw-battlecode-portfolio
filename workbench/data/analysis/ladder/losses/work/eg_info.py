# Scratch (early-growth brief): which games, which layouts, what the starting position looks like.
import sys, json
from collections import Counter
from pathlib import Path

per = json.loads(Path('data/analysis/ladder/losses/split/per-game.json').read_text())
maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())
print('per-game records', len(per), 'keys', sorted(per[0].keys()))
print('side keys', sorted(per[0]['sides']['us'].keys()))
c = Counter()
for r in per:
    L = r['sides']['us']['starting_dragons'][0]['initial_length']
    c[(r['map_key'], r['group'], L)] += 1
for k, n in sorted(c.items(), key=lambda kv: str(kv[0])):
    print(k, n)
for key in sorted({r['map_key'] for r in per}):
    m = maps.get(key)
    if m is None:
        print(key, 'not in maps.json')
        continue
    print(key, {k: (v if not isinstance(v, (list, dict)) or len(str(v)) < 200 else '...') for k, v in m.items()})
sel = [r for r in per if r['group'] == 'never_grew' and r['sides']['us']['starting_dragons'][0]['initial_length'] == 2]
print('selected', len(sel), Counter(r['map_key'] for r in sel), Counter(r['result'] for r in sel))
print(sel[0]['replay'], sel[0]['game'], sel[0]['battle'])

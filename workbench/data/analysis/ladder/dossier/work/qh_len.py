"""Scratch (diag-queenhit): queen length. Boxed turns (no clean tile, a ring on a tile) by her length and outcome;
routine splits; and her length on paper if a routine split had to leave her 3 (same pearls, same paid steps, same
emergency splits; a routine split waits until she is 5)."""
import sys
import json
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
KEEP = 3
fates = dict((f['game'], f) for f in json.loads((WORK / 'qh_fates.json').read_text()))
turns = defaultdict(list)
with (WORK / 'qh_turns.jsonl').open() as fh:
    for line in fh:
        t = json.loads(line)
        turns[t['game']].append(t)
hits = [g for g, f in fates.items() if f['fate'] and not f['fate']['mover'] and f['fate']['cause'] == 'head-on']


def routine(t):
    enter = [x for x in t['cands'] if x.get('enterable')]
    return any(not x['closed'] for x in enter) and not t['risky']


c = Counter()
paper = {}
for g, ts in turns.items():
    L2 = ts[0]['L']
    for k, t in enumerate(ts):
        t['paper_L'] = L2
        a = t.get('action') or {}
        dead = t['hit_after'] is not None
        if t['round'] <= 300:
            c['turns r0-300'] += 1
            c['turns r0-300 at 2'] += t['L'] == 2
            c['paper turns r0-300 at 2'] += L2 == 2
        if t['hit_blocked']:
            key = 'boxed at 2' if t['L'] == 2 else 'boxed at 3+'
            c[key] += 1
            c[key + ', hit followed'] += dead
            if t['L'] == 2:
                c['boxed at 2, clean tile two steps away'] += t['sprint2']
                c['boxed at 2, clean tile two steps away, hit followed'] += t['sprint2'] and dead
                c['boxed at 2, clean tile two steps away, on paper 3+'] += t['sprint2'] and L2 >= 3
                c['boxed at 2, clean tile two steps away, hit followed, on paper 3+'] += t['sprint2'] and dead and L2 >= 3
            else:
                c['boxed at 3+, paid a segment'] += a.get('kind') == 'move' and t.get('L_after', 0) < t['L']
        if t.get('end') is None and not dead:
            continue
        after = t.get('L_after', t['L'])
        if a.get('kind') == 'split':
            child = t['L'] - after
            c['splits'] += 1
            if routine(t):
                c['routine splits'] += 1
                c['routine splits leaving 2'] += after == 2
                if L2 - 2 >= KEEP:
                    L2 -= 2
                    c['paper routine splits'] += 1
            elif L2 - child >= 2:
                L2 -= child
        elif after:
            L2 = max(2, L2 + after - t['L'])
for g in hits:
    t = turns[g][-1]
    print('  ', g, fates[g]['map'], 'L', t['L'], 'on paper', t['paper_L'], 'boxed', t['hit_blocked'], 'clean tile two steps away', t['sprint2'])
print(dict(c))

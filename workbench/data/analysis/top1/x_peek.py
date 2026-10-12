#!/usr/bin/env python3
"""Peek at games.csv: counts by team, battle_id, opponents (2000+, no Schooltime)."""
import csv, collections, sys
rows = list(csv.DictReader(open('games.csv')))
print('rows', len(rows))
print('cols', list(rows[0].keys()))
TOP = {'306': 'Vibing++', '91': 'SSS', '264': 'forgot', '1119': 'meow'}
def side(r, tid):
    return 'A' if r['teamAId'] == tid else ('B' if r['teamBId'] == tid else None)
for tid, name in TOP.items():
    n = 0; n2 = 0; w = 0
    bat = collections.Counter(); opp = collections.Counter()
    for r in rows:
        s = side(r, tid)
        if not s: continue
        n += 1
        o = 'B' if s == 'A' else 'A'
        oelo = float(r['team%sElo' % o] or 0)
        if oelo >= 2000 and r['map'] != 'Schooltime':
            n2 += 1
            w += r['winner'] == s
            bat[r['battle_id']] += 1
            opp[(r['team%sId' % o], r['team%sName' % o])] += 1
    print(name, 'all', n, '2000+ noSchool', n2, 'won', w)
    if tid == '1119':
        for k, v in sorted(bat.items()): print('   ', k, v)
    for k, v in opp.most_common(12): print('      opp', k, v)
print(collections.Counter(r['end_type'] for r in rows))
print(collections.Counter(r['map_size'] for r in rows))
print(collections.Counter(r['sources'] for r in rows).most_common(10))
m = collections.Counter((r['map'], r['cells']) for r in rows)
for k, v in sorted(m.items(), key=lambda kv: int(kv[0][1])): print(k, v)

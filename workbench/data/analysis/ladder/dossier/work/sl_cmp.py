# Scratch (diag-split): compares sl_recount-*.jsonl (stock parser) with sl_scan-*.jsonl game by game. Prints only.
# Usage: python3 data/analysis/ladder/dossier/work/sl_cmp.py
import json
from collections import Counter

D = 'data/analysis/ladder/dossier/work/'
scan = {}
for k in range(4):
    for line in open(D + 'sl_scan-%d.jsonl' % k):
        g = json.loads(line)
        scan[(g['tm'], g['game'])] = g
n = bad = 0
tot = {'O': Counter(), 'R': Counter()}
for k in range(2):
    for line in open(D + 'sl_recount-%d.jsonl' % k):
        r = json.loads(line)
        g = scan[(r['tm'], r['game'])]
        by = [0] * 5
        for b in range(6):
            for ln in range(2, 17):
                by[0 if ln == 2 else 1 if ln == 3 else 2 if ln == 4 else 3 if ln <= 7 else 4] += g['lhist'][b][ln]
        p4 = child2 = rem2 = 0
        for key, v in g['splen'].items():
            bd, pl, c = map(int, key.split(','))
            p4 += v * (pl == 4)
            child2 += v * (c == 2)
            rem2 += v * (pl < 16 and c < 12 and pl - c == 2)
        mine = dict(turns=sum(g['turns'][0]), ge4=sum(v[0] for v in g['elig'].values()), by=by, splits=sum(g['splits'][0]),
                    p4=p4, child2=child2, deaths=sum(g['deathsn'][0]))
        n += 1
        diff = [f for f in mine if mine[f] != r[f]]
        if diff:
            bad += 1
            if bad <= 10:
                print('MISMATCH', r['tm'], r['game'], [(f, mine[f], r[f]) for f in diff])
        t = tot[r['tm']]
        t['games'] += 1
        for f in ('turns', 'ge4', 'splits', 'p4', 'child2', 'rem2', 'deaths'):
            t[f] += r[f]
        t['rem2_scan'] += rem2
print('games compared', n, 'with any difference', bad)
for tm in 'OR':
    t = tot[tm]
    print(tm, dict(t), 'splits/1k turns %.2f' % (1000 * t['splits'] / t['turns']), 'share of turns at 4+ %.2f%%' % (100 * t['ge4'] / t['turns']),
          'splits per 100 turns at 4+ %.2f' % (100 * t['splits'] / t['ge4']), 'deaths/1k %.2f' % (1000 * t['deaths'] / t['turns']),
          'parent keeps 2: recount %.1f%% scan %.1f%%' % (100 * t['rem2'] / t['splits'], 100 * t['rem2_scan'] / t['splits']))

import sys, json
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from statistics import median
ROOT = '~/01. Project/개인 프로젝트/unsw-swarm/'
obs = json.load(open(ROOT + 'data/analysis/ladder/map-observations.json'))
gaps = json.load(open('gaps.json'))
by = defaultdict(list)
for o in obs.values(): by[o['map']].append(o)
print(f"{'map':16s} {'true(rate)':>10s} {'true(births)':>12s} {'estimate':>9s}  fast tiles true/est/both  est-fast tiles by true gap")
for m in ('Around UNSW', 'Australia', 'Portals', 'Trauma', 'Devil', 'Queen Of Spades'):
    g = {k: tuple(v) for k, v in gaps[m]['gaps'].items()}
    births = Counter(); iv = defaultdict(list)
    for o in by[m]:
        births.update(o['natural'])
        for c, vs in o['intervals'].items(): iv[c].extend(vs)
    fast_est = {c for c, vs in iv.items() if len(vs) >= 5 and median(vs) <= 12}
    fast_true = {c for c, (lo, hi) in g.items() if 1 <= hi <= 12}
    rate = {c: 2 / (lo + hi) for c, (lo, hi) in g.items()}
    true_rate = sum(rate[c] for c in fast_true) / sum(rate.values())
    tb = sum(births[c] for c in fast_true) / sum(births.values())
    est = sum(births[c] for c in fast_est) / sum(births.values())
    kinds = Counter(g.get(c, 'never') for c in fast_est)
    print(f"{m:16s} {true_rate:10.3f} {tb:12.3f} {est:9.3f}  {len(fast_true)}/{len(fast_est)}/{len(fast_true & fast_est)}  {dict(kinds)}")

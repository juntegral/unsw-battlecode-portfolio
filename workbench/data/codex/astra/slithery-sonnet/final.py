"""Summary counts per map. Usage: final.py"""
import sys
from collections import Counter
sys.path.insert(0, '~/01. Project/개인 프로젝트/unsw-swarm/data/codex/astra/slithery-sonnet/')
import table
SL = sys.argv[1] if len(sys.argv) > 1 else 'all'
for m in ('Slithery Fight', 'Portals'):
    rows = [r for r in table.rows if r['map'] == m and (SL == 'all' or r['ranked'])]
    print('=====', m, len(rows), 'games', Counter(r['result'] for r in rows), 'by src', Counter(r['src'][:6] for r in rows))
    print(' by version', {v: dict(Counter(r['result'] for r in rows if table.VER[r['bot']] == v)) for v in sorted({table.VER[r['bot']] for r in rows}, key=lambda x: int(x[3:]))})
    print(' loss classes', dict(Counter(table.klass(r) for r in rows if r['result'] == 'loss')))
    print(' how decided (all games)', dict(Counter((r['result'], r['how']) for r in rows)))
    # queen survival
    for s, lab in ((0, 'us'), (1, 'them')):
        alive = [r for r in rows if r['ends'][s][3] > 0]
        print(' %s queen alive at end: %d/%d; in wins %d/%d, in losses %d/%d' % (lab, len(alive), len(rows),
              sum(1 for r in alive if r['result'] == 'win'), sum(1 for r in rows if r['result'] == 'win'),
              sum(1 for r in alive if r['result'] == 'loss'), sum(1 for r in rows if r['result'] == 'loss')))
    # first queen death round distribution
    for s, lab in ((0, 'us'), (1, 'them')):
        fr = []
        for r in rows:
            qd = [d[0] for d in r['deaths'] if d[1] == s and d[6]]
            fr.append(min(qd) if qd else None)
        died = [x for x in fr if x is not None]
        print(' %s queen first-death rounds: <100:%d 100-299:%d 300+:%d none:%d' % (lab, sum(x < 100 for x in died), sum(100 <= x < 300 for x in died), sum(x >= 300 for x in died), fr.count(None)))
    # who died first
    both = Counter()
    for r in rows:
        f = [min([d[0] for d in r['deaths'] if d[1] == s and d[6]] or [9999]) for s in (0, 1)]
        both['us first' if f[0] < f[1] else 'them first' if f[1] < f[0] else 'none/tie'] += 1
    print(' first queen to die (all games)', dict(both))
    both = Counter()
    for r in rows:
        f = [min([d[0] for d in r['deaths'] if d[1] == s and d[6]] or [9999]) for s in (0, 1)]
        both[(r['result'], 'us first' if f[0] < f[1] else 'them first' if f[1] < f[0] else 'none')] += 1
    print(' result by first queen to die', dict(both))
    # queen split-to-2 of a big queen followed by death within 3 rounds
    n = 0; nq = 0
    for r in rows:
        sp = [x for x in r['splits'] if x[1] == 0 and x[5] and x[2] >= 8 and x[3] == 2]
        qd = [d[0] for d in r['deaths'] if d[1] == 0 and d[6]]
        for x in sp:
            n += 1
            if any(0 <= d - x[0] <= 3 for d in qd):
                nq += 1
    print(' our queen (>=8) splits down to 2: %d, of which queen dead within 3 rounds: %d' % (n, nq))
    nd = sum(1 for r in rows if any(d[1] == 0 and d[6] for d in r['deaths']))
    print(' our queen died in %d of %d games' % (nd, len(rows)))

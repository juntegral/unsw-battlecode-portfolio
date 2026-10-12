"""opp-uncancel: deaths by side/kind in round windows, and ram exchanges. Usage: deaths.py <gid> ..."""
import sys, json, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
import o1_scan
from pathlib import Path
from collections import Counter

for g in sys.argv[1:]:
    gid = int(g)
    mp = [Path(f) for f in glob.glob('data/online/live-one1/b*/game-%d.json' % gid)][0]
    j = json.load(open(mp))
    row = o1_scan.scan('x', mp.parent / ('M%d.replay' % gid), j)
    print('===', gid, j['mapName'], row['result'], 'cells', row['cells'])
    for lo, hi in ((0, 50), (50, 100), (100, 200), (200, 500)):
        c = Counter()
        for d in row['deaths']:
            if lo <= d[0] < hi:
                c[('us' if d[1] == 0 else 'them', d[4])] += 1
        print('  r%d-%d' % (lo, hi), dict(sorted(c.items())))
    e = [[sum(1 for x in row['eats'] if lo <= x[0] < lo + 25 and x[1] == k and x[3] == 'n') for lo in (0, 25, 50, 75)] for k in (0, 1)]
    print('  natural pearls per 25r (r0-100) us', e[0], 'them', e[1])
    print('  sample death rec:', row['deaths'][0] if row['deaths'] else None)

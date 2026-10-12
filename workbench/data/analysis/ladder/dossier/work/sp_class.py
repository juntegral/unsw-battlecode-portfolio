# Scratch (diag-spawn): pools sp_t-*.jsonl by layout and gives every spawning tile a class by its mean
# gap between spawn attempts, estimated as free round-starts / births (rounds 0-300). Writes sp_tiles.json.
# Classes: 0 every round (gap under 1.5), 1 gap 1.5-4, 2 gap 4-8, 3 gap 8-25, 4 gap 25-80, 5 gap 80+.
# Cross-check against the reconstructed TILE lines of the 9 layouts in dossier/local/maps2 and maps3.
# Usage: python3 data/analysis/ladder/dossier/work/sp_class.py
import sys, json
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
KNOWN = {'Islands #1': 'maps2/ladder_islands_1.map', 'Australia #1': 'maps2/ladder_australia_1.map',
         'Around UNSW #1': 'maps2/ladder_around_unsw_1.map', 'Slithery Fight #1': 'maps2/ladder_slithery_fight_1.map',
         'Schooltime #1': 'maps2/ladder_schooltime_1.map', 'Schooltime #2': 'maps2/ladder_schooltime_2.map',
         'Stripes #1': 'maps3/ladder_stripes_1.map', 'Portals #1': 'maps3/ladder_portals_1.map',
         'Tower Defense #1': 'maps3/ladder_tower_defense_1.map'}


def klass(g):
    return 0 if g < 1.5 else 1 if g < 4 else 2 if g < 8 else 3 if g < 25 else 4 if g < 80 else 5


births = defaultdict(Counter)
free = {}
games = Counter()
dims = {}
for n in range(6):
    p = Path(OUT + 'sp_t-%d.jsonl' % n)
    for line in p.read_text().splitlines():
        r = json.loads(line)
        k = r['layout']
        games[k] += 1
        dims[k] = (r['w'], r['h'])
        for t, b in r['births'].items():
            births[k][int(t)] += b
        if k not in free:
            free[k] = [0] * len(r['free'])
        f = free[k]
        for t, v in enumerate(r['free']):
            f[t] += v
cls, stat = {}, {}
for k in sorted(games):
    table = {}
    for t, b in births[k].items():
        g = free[k][t] / b
        table[t] = klass(g)
    cls[k] = table
    cc = Counter(table.values())
    stat[k] = dict(games=games[k], cells=len(free[k]), per_class=[cc.get(c, 0) for c in range(6)])
    line = '%-22s games %3d cells %4d  classes 0..5: %s' % (k, games[k], len(free[k]), stat[k]['per_class'])
    if k in KNOWN:
        w, h = dims[k]
        conf = Counter()
        for row in Path('data/analysis/ladder/dossier/local/' + KNOWN[k]).read_text().splitlines():
            q = row.split()
            if q and q[0] == 'TILE' and len(q) == 5:
                x, y, lo, hi = map(int, q[1:])
                t = y * w + x
                want = -1 if hi == 0 else klass((lo + hi) / 2)
                conf[(want, table.get(t, -1))] += 1
        ok = sum(v for (a, b), v in conf.items() if a == b and a >= 0)
        tot = sum(v for (a, b), v in conf.items() if a >= 0)
        off = {('%d>%d' % a): v for a, v in sorted(conf.items()) if a[0] != a[1]}
        line += '  | known map: same class %d of %d spawning tiles; differ (known>measured) %s' % (ok, tot, off)
    print(line)
Path(OUT + 'sp_tiles.json').write_text(json.dumps(dict(cls=cls, stat=stat)))
print('written')

"""t.py <arm off> <arm on>: per map and seat, our natural pearls and units at r100, queen death round, result. Run from ROOT."""
import sys, json, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from pathlib import Path
from o1_scan import scan
RUNS = Path.home() / 'meow-redteam/solo/runs'


def row(arm, name):
    folder = RUNS / arm / name
    if not (folder / 'result.txt').exists():
        return None
    m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', name)
    k = int(m[3])
    j = dict(id=0, teamAId=1119 if k == 0 else 1, teamBId=1 if k == 0 else 1119, mapName=m[1], teamAName='A', teamBName='B')
    g = scan(arm, folder / 'game.replay', j)
    ks = sorted(int(x) for x in g['snaps'])
    sn = g['snaps'][str(max([x for x in ks if x <= 100] or [ks[0]]))]
    p = sum(1 for e in g['eats'] if e[1] == 0 and e[3] == 'n' and e[0] <= 100)
    po = sum(1 for e in g['eats'] if e[1] == 1 and e[3] == 'n' and e[0] <= 100)
    qd = min((d[0] for d in g['deaths'] if d[1] == 0 and d[6]), default=-1)
    return 'p%3d u%2d T%3d (opp p%3d u%2d) qdead %3d %-4s end T%3d Q%2d v T%3d Q%2d' % (
        p, sn[0][0], sn[0][1], po, sn[1][0], qd, g['result'], g['ends'][0][1], g['ends'][0][3], g['ends'][1][1], g['ends'][1][3])


off, on = sys.argv[1], sys.argv[2]
for name in sorted({f.name for a in (off, on) for f in (RUNS / a).glob('*-seed*-side*')}):
    print(name)
    for lab, arm in (('off', off), ('on ', on)):
        print('   ', lab, row(arm, name))

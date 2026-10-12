"""m.py online | <arm> ... : Trauma start table, both sides, same script. Run from ROOT."""
import sys, json, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from pathlib import Path
from o1_scan import scan
SM = Path('data/online/smoke')
RUNS = Path.home() / 'meow-redteam/solo/runs'


def snap(g, r):
    ks = sorted(int(k) for k in g['snaps'])
    k = max([x for x in ks if x <= r] or [ks[0]])
    return g['snaps'].get(k, g['snaps'].get(str(k)))


def show(label, g):
    for s, nm in ((0, 'us '), (1, 'opp')):
        nat = [e for e in g['eats'] if e[1] == s and e[3] == 'n']
        first = min((e[0] for e in nat), default=-1)
        cells = []
        for r in (25, 50, 100, 150):
            sn = snap(g, r)[s]
            cells.append('r%d p%d u%d T%d Q%d' % (r, sum(1 for e in nat if e[0] <= r), sn[0], sn[1], sn[3]))
        sp = [x for x in g['splits'] if x[1] == s and x[0] <= 100]
        qsp = [x[0] for x in sp if x[5]]
        print('%-34s %s first %3d | %s | splits<=100 %d (queen at %s) first5 %s' % (label, nm, first, ' | '.join(cells), len(sp), qsp[:6], [(x[0], x[2], x[3], x[4]) for x in sp[:5]]))
    print('   last', g['last'], 'ends', [e[:4] for e in g['ends']], g.get('how'), g.get('won'))


if sys.argv[1] == 'online':
    for f in ('one15-c1-old', 'one15-p1-old', 'one15-s1-old', 'one16-c1-old'):
        for mp in sorted((SM / f).glob('game-*.json')):
            j = json.loads(mp.read_text())
            if j.get('mapName') != 'Trauma':
                continue
            rp = SM / f / ('M%d.replay' % j['id'])
            if not rp.exists():
                continue
            g = scan(f, rp, j)
            opp = j['teamBName'] if j['teamAId'] == 1119 else j['teamAName']
            show('%s %d seat%d v %s' % (f[:8], j['id'], 0 if j['teamAId'] == 1119 else 1, opp[:10]), g)
else:
    for arm in sys.argv[1:]:
        for folder in sorted((RUNS / arm).glob('*-seed*-side*')):
            if not (folder / 'result.txt').exists():
                continue
            m = re.fullmatch(r'(.+)-seed(\d+)-side(\d)', folder.name)
            k = int(m[3])
            j = dict(id=0, teamAId=1119 if k == 0 else 1, teamBId=1 if k == 0 else 1119, mapName=m[1], teamAName='A', teamBName='B')
            g = scan(arm, folder / 'game.replay', j)
            show('%s %s s%d' % (arm, m[1][7:20], k), g)

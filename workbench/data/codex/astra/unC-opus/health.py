"""unC-opus: one health line per finished game folder. Usage (ROOT): python3 -B data/codex/astra/unC-opus/health.py <folder> ...
Each folder holds game.replay, result.json, engine.log. Our seat = side digit in the folder name (default 0)."""
import sys, json, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from pathlib import Path
from collections import Counter
from o1_scan import scan


def snap(g, r):
    ks = sorted(int(k) for k in g['snaps'])
    k = max([x for x in ks if x <= r], default=ks[0])
    return g['snaps'][str(k)]


def line(folder):
    folder = Path(folder)
    if not (folder / 'result.json').exists():
        return '%-34s (not finished)' % folder.name
    res = json.loads((folder / 'result.json').read_text())
    m = re.search(r'side(\d)', folder.name)
    k = int(m[1]) if m else 0
    j = dict(id=0, teamAId=1119 if k == 0 else 1, teamBId=1 if k == 0 else 1119, mapName=folder.name, teamAName='A', teamBName='B')
    try:
        g = scan('uc', folder / 'game.replay', j)
    except Exception as e:
        return '%-34s SCAN FAIL %r  %s' % (folder.name, e, res['line'])
    log = (folder / 'engine.log').read_text().splitlines()
    why = Counter()
    for l in log:
        mm = re.match(r'round \d+: dragon \d+, team (\w): (.+)', l)
        if mm:
            why[(mm[1], mm[2])] += 1
    mine = 'AB'[k]
    out = []
    for s in (0, 1):
        t = mine if s == 0 else 'AB'[1 - k]
        eats = [e[0] for e in g['eats'] if e[1] == s]
        fe = min(eats, default=-1)
        pe = [sum(1 for r in eats if r <= x) for x in (25, 50, 100)]
        dr = [snap(g, x)[s][0] for x in (25, 50, 100)]
        ql = [snap(g, x)[s][3] for x in (100, 300)] + [g['ends'][s][3]]
        qd = [d for d in g['deaths'] if d[1] == s and d[6]]
        q = 'alive' if not qd else 'dead r%d %s free%d L%d' % (qd[0][0], qd[0][4], qd[0][5], qd[0][2])
        kinds = Counter(d[4] for d in g['deaths'] if d[1] == s)
        out.append('%s eat1 r%d pearls %s drag %s q %s qL %s deaths %s nva %d' % (
            'US ' if s == 0 else 'OPP', fe, '/'.join(map(str, pe)), '/'.join(map(str, dr)), q, '/'.join(map(str, ql)),
            dict(kinds), why[(t, 'no valid action')]))
    return '%-34s %s %s r%d %.0fs err%d\n    %s\n    %s' % (folder.name, g['result'], g['how'], g['last'], res['seconds'], len(res['bot_errors']), out[0], out[1])


for f in sys.argv[1:]:
    print(line(f))

"""unC-opus: per-game detail. Usage (ROOT): python3 -B data/codex/astra/unC-opus/detail.py <folder> [rounds...]"""
import sys, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from pathlib import Path
from collections import Counter
from o1_scan import scan
f = Path(sys.argv[1])
m = re.search(r'side(\d)', f.name)
k = int(m[1]) if m else 0
g = scan('uc', f / 'game.replay', dict(id=0, teamAId=1119 if k == 0 else 1, teamBId=1 if k == 0 else 1119, mapName='x', teamAName='A', teamBName='B'))
print(f.name, g['result'], g['how'], 'last', g['last'])
rs = [int(x) for x in sys.argv[2:]] or sorted(int(x) for x in g['snaps'])
for r in rs:
    s = g['snaps'].get(str(r))
    if s:
        print(' r%d US n,total,longest,queen %s OPP %s' % (r, s[0][:4], s[1][:4]))
for s in (0, 1):
    e = [x for x in g['eats'] if x[1] == s]
    print(' side', 'US' if s == 0 else 'OPP', 'eats', len(e), dict(Counter(x[3] for x in e)), 'by role', dict(Counter(x[2] for x in e)))
    print('  deaths (r,L,kind,queen,free)', [(d[0], d[2], d[4], d[6], d[5]) for d in g['deaths'] if d[1] == s][:30])
    sp = [x for x in g['splits'] if x[1] == s]
    print('  splits', len(sp), '(r,Lbefore,parent,child,queen)', [(x[0], x[2], x[3], x[4], x[5]) for x in sp][:14])
    pd = [x for x in g['paids'] if x[1] == s]
    print('  paid turns', len(pd), 'queen paid', [(x[0], x[2], x[3]) for x in pd if x[6]][:12])

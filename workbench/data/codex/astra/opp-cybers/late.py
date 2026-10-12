"""opp-cybers: the end race in the long games, both sides. Usage (ROOT): python3 -B late.py <gameid> ..."""
import sys, json, glob
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
import o1_scan
from collections import Counter
from pathlib import Path

for gid in map(int, sys.argv[1:]):
    mp = [Path(f) for f in glob.glob('data/online/live-one1/b*/game-%d.json' % gid)][0]
    j = json.load(open(mp))
    row = o1_scan.scan(mp.parent.name, mp.parent / ('M%d.replay' % gid), j)
    sn = row['snaps']
    ks = [k for k in ('300', '350', '375', '400', '425', '450', '475') if k in sn] + [sorted(sn, key=int)[-1]]
    print('=== %d %s %s' % (gid, j['mapName'], row['result']))
    print('  longest us  :', ' '.join('r%s %d' % (k, sn[k][0][2]) for k in ks))
    print('  longest them:', ' '.join('r%s %d' % (k, sn[k][1][2]) for k in ks))
    print('  dragons us  :', ' '.join('r%s %d' % (k, sn[k][0][0]) for k in ks))
    print('  dragons them:', ' '.join('r%s %d' % (k, sn[k][1][0]) for k in ks))
    for s, nm in ((0, 'us  '), (1, 'them')):
        late = Counter(d[4] for d in row['deaths'] if d[1] == s and d[0] >= 400)
        big = [(d[0], d[2], d[4]) for d in row['deaths'] if d[1] == s and d[2] >= 8]
        bigk = Counter(k for _, _, k in big)
        print('  %s deaths r>=400 by kind: %s' % (nm, dict(late.most_common(6))))
        print('  %s dragons of 8+ lost, whole game: %d  by kind %s  rammed ones (round,len): %s' % (
            nm, len(big), dict(bigk), [(r, L) for r, L, k in big if k == 'rammed']))

"""unD-opus: deaths by kind and side in round bands, for <arm>/<folder> ... (run from ROOT)."""
import sys, re
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from pathlib import Path
from collections import Counter
import o1_scan
RUNS = Path.home() / 'meow-redteam/solo/runs'
for spec in sys.argv[1:]:
    arm, folder = spec.split('/')
    k = int(folder[-1])
    j = dict(id=0, teamAId=1119 if k == 0 else 1, teamBId=1 if k == 0 else 1119, mapName=folder, teamAName='A', teamBName='B')
    g = o1_scan.scan(arm, RUNS / arm / folder / 'game.replay', j)
    print(spec, g['result'], g['how'], g['last'])
    for lo, hi in ((0, 15), (16, 30), (31, 45), (46, 60), (61, 100)):
        row = []
        for s in (0, 1):
            c = Counter(d[4] for d in g['deaths'] if d[1] == s and lo <= d[0] <= hi)
            L = sum(d[2] for d in g['deaths'] if d[1] == s and lo <= d[0] <= hi)
            row.append('%s len %d %s' % ('US' if s == 0 else 'OP', L, dict(c)))
        sn = g['snaps'].get(str(min(hi if hi % 25 == 0 else (hi // 25) * 25, g['last'])))
        print('  r%d-%d  %s | %s' % (lo, hi, row[0], row[1]))
    print('  units,total at r25/r50/r75:', [(g['snaps'][str(r)][0][:2], g['snaps'][str(r)][1][:2]) for r in (25, 50, 75) if str(r) in g['snaps']])

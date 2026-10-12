"""Game 1532570 (Islands, we are team A): what happens to our dragons around round 469."""
import sys, json, os
sys.dont_write_bytecode = True
os.chdir('~/01. Project/개인 프로젝트/unsw-swarm')
sys.path.insert(0, 'tools'); sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from o1_scan import scan
d = 'data/online/live-one1/b1532570/'
g = scan('x', d + 'M1532570.replay', json.load(open(d + 'game-1532570.json')))
print(sorted(g.keys()))
for k in ('deaths', 'rams', 'longdeaths'):
    v = g.get(k)
    if isinstance(v, list):
        print(k, len(v))
        for row in v:
            s = json.dumps(row)
            if any(('%d' % r) in s.split(',')[0] or (isinstance(row, (list, tuple)) and row and row[0] in range(462, 474)) for r in range(462, 474)):
                print('  ', s[:220])

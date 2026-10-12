"""Scratch (meow-main07): early deaths of our own making. For every game in the given folders: our and their deaths in r0-40
by cause, and games where a dragon died on a mate (body or head) before r41. Usage: o1_matedeath.py <folder>..."""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/analysis/ladder/dossier/work')
from pathlib import Path
from collections import Counter, defaultdict
from o1_scan import scan
tot = defaultdict(lambda: [0, Counter(), Counter(), 0, 0])
rows = []
for folder in sys.argv[1:]:
    folder = Path(folder)
    for mp in sorted(folder.glob('game-*.json')):
        j = json.loads(mp.read_text())
        rp = folder / ('M%d.replay' % j['id'])
        if not rp.exists() or 1119 not in (j['teamAId'], j['teamBId']):
            continue
        try:
            g = scan(folder.name, rp, j)
        except Exception as e:
            continue
        key = str(g.get('bot'))
        t = tot[key]
        t[0] += 1
        hit = [False, False]
        for d in g['deaths']:
            if d[0] <= 40:
                t[1 + d[1]][d[4]] += 1
                if d[4] in ('mate body', 'mate head'):
                    hit[d[1]] = True
                    if d[1] == 0:
                        rows.append((key, j['id'], j['mapName'], d[0], d[2], d[4], d[-1], g.get('result')))
        t[3] += hit[0]
        t[4] += hit[1]
out = ['bot | games | games with an early mate death ours/theirs | our r0-40 deaths by cause | theirs']
for k in sorted(tot):
    t = tot[k]
    out.append('%s | %d | %d/%d | %s | %s' % (k, t[0], t[3], t[4], dict(t[1]), dict(t[2])))
out.append('our early mate deaths: bot, game, map, round, length, cause, cell, result')
for r in rows:
    out.append(' '.join(str(x) for x in r))
open('data/analysis/ladder/dossier/work/o1_matedeath.out', 'w').write('\n'.join(out) + '\n')
print('\n'.join(out[:14]))

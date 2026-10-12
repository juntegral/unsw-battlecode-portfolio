# Scratch (diag-med20): quick look at the to_scan rows already on disk: medium layouts, pearls by r10/r20 per layout.
import sys, json
from pathlib import Path
from collections import defaultdict

W = Path('data/analysis/ladder/dossier/work')
NAMES = {454: 'aAah', 157: 'larp', 306: 'Cutlery', 70: 'chad', 1119: 'ours'}
acc = defaultdict(list)
maps = {}
for f in sorted(W.glob('to_scan-*.jsonl')):
    tag = f.name[8:].split('-')[0]
    if tag in ('test', 'T1'):
        continue
    for line in f.read_text().splitlines():
        r = json.loads(line)
        if 'error' in r or not 700 < r['cells'] <= 1200:
            continue
        maps[r['map']] = (r['w'], r['h'], r['pairs'], r['walls'])
        for s in 'ut':
            sd = r['sides'][s]
            who = (tag if sd['team'] == 1119 else NAMES.get(sd['team'], 'x')) if s == 'u' else 'opp-of-' + tag
            if s == 't' and tag == 'OT':
                who = 'direct-' + NAMES.get(sd['team'], str(sd['team']))
            v = sd['series']
            if len(v['eaten']) <= 20:
                continue
            acc[(r['map'], who)].append((v['eaten'][10], v['eaten'][20], v['nat'][20], v['alive'][0], v['alive'][10], v['alive'][20], v['total'][20], str(sd['cfg'])))
print(maps)
for key in sorted(acc):
    v = acc[key]
    n = len(v)
    m = lambda k: sum(x[k] for x in v) / n
    print('%-28s %-16s n=%3d e10 %.2f e20 %.2f nat20 %.2f alive0 %.2f a10 %.2f a20 %.2f len20 %.1f cfg %s' % (key[0][:28], key[1], n, m(0), m(1), m(2), m(3), m(4), m(5), m(6), v[0][7]))

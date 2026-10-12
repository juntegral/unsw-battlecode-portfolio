"""stuck-opus: loop share by version with and without the Portals map, and on the maps of 2,000+ cells. Usage (ROOT): python3 -B data/codex/astra/stuck-opus/noportal.py"""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from collections import defaultdict
HERE = Path('data/codex/astra/stuck-opus')
CATS = ('deadend', 'free', 'mate', 'enemy', 'idle')
gs = []
for p in sorted(HERE.glob('rows-one*.jsonl')):
    gs += [json.loads(l) for l in p.read_text().splitlines()]
for name, keep in (('all maps', lambda g: True), ('without Portals', lambda g: g['map'] != 'Portals'), ('maps of 2000+ cells', lambda g: g['cells'] >= 2000 and g['map'] != 'Portals'),
                   ('maps under 2000 cells, no Portals', lambda g: g['cells'] < 2000 and g['map'] != 'Portals')):
    print(name)
    acc = defaultdict(lambda: [0, 0, 0, 0, 0, defaultdict(int), defaultdict(int)])
    for g in gs:
        if not keep(g):
            continue
        a = acc[g['ver']]
        a[4] += 1
        for s in (0, 1):
            a[1 + 2 * s] += sum(g['cnt'][s][ro][ph]['n'] for ro in range(2) for ph in range(3))
            for ph in range(3):
                for c, v in g['lc'][s][ph].items():
                    a[2 * s] += v
                    a[5 + s][c] += v
    for k in sorted(acc):
        a = acc[k]
        print('  %-6s n=%-3d ours %4.1f%% (%5.0f a game) theirs %4.1f%% | ours by class %s | theirs %s' % (
            k, a[4], 100 * a[0] / max(a[1], 1), a[0] / a[4], 100 * a[2] / max(a[3], 1),
            ' '.join('%s %.1f' % (c, 100 * a[5][c] / max(a[1], 1)) for c in CATS), ' '.join('%s %.1f' % (c, 100 * a[6][c] / max(a[3], 1)) for c in CATS)))

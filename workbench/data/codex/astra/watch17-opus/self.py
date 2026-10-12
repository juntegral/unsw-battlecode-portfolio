"""watch17-opus: queen deaths on her own move (wall / own body) per build. Usage (from ROOT): python3 -B .../self.py"""
import json
from collections import defaultdict
from pathlib import Path
C = json.loads(Path('data/codex/astra/watch17-opus/cache.json').read_text())
RS = {0: 'wall', 1: 'own', 2: 'body', 3: 'headon', 4: 'other'}
by = defaultdict(list)
for g in C.values():
    if g.get('ver'):
        by[g['ver']].append(g)
print('build  games wins losses | queen dead | on wall/own: all games, in losses | timeouts collapses(us) | shed 10+ to 2 | q 10+ killed')
for v in sorted(by):
    gs = by[v]
    L = [g for g in gs if g['win'] is False]
    so = [g for g in gs if g['qdead'] and g['qdead'][2] in (0, 1)]
    print('%-6s %5d %4d %6d | %10d | %8d of %d games, %d of %d losses | %8d %10d | %13d | %d' % (
        v, len(gs), sum(1 for g in gs if g['win']), len(L), sum(1 for g in gs if g['qdead']), len(so), len(gs),
        sum(1 for g in so if g['win'] is False), len(L), sum(g['acts'][0].get('timeout', 0) for g in gs),
        sum(1 for g in gs for c in g['collapse'] if c[1]),
        sum(1 for g in gs for s in g['qsplits'] if s['before'] >= 10 and s['after'] == 2),
        sum(1 for g in gs if g['qdead'] and g['qdead'][1] >= 10)))
print()
for v in ('one18', 'one19', 'one20'):
    for g in sorted(by.get(v, []), key=lambda g: g['id']):
        if g['qdead'] and g['qdead'][2] in (0, 1):
            print(v, g['id'], g['map'], g['opp'], 'WIN' if g['win'] else 'LOSS', 'queen died r%d len %d on %s' % (g['qdead'][0], g['qdead'][1], RS[g['qdead'][2]]))

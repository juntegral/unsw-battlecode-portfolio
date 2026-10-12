"""watch17-opus: games where our queen died at length >= 10, with paths. Usage (from ROOT): python3 -B .../longq.py"""
import json, glob
from pathlib import Path
C = json.loads(Path('data/codex/astra/watch17-opus/cache.json').read_text())
RS = {0: 'wall', 1: 'own', 2: 'body', 3: 'headon', 4: 'other'}
idx = {}
for f in glob.glob('data/online/smoke/one1[5-9]-*-old/game-*.json') + glob.glob('data/online/live-one1/b*/game-*.json'):
    idx[Path(f).stem.split('-')[1]] = f
for k, g in sorted(C.items()):
    if g.get('ver') and g['qdead'] and g['qdead'][1] >= 10:
        print(g['ver'], g['set'], k, g['map'], 'r%d len %d %s' % (g['qdead'][0], g['qdead'][1], RS.get(g['qdead'][2])), 'WIN' if g['win'] else 'LOSS', idx[k])

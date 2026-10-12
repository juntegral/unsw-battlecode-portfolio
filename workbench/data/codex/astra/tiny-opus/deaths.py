"""Our deaths in the first 110 rounds of online games: python3 -B data/codex/astra/tiny-opus/deaths.py <game json> ..."""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/codex/astra/early-opus')
from pathlib import Path
import scan as S
for p in sys.argv[1:]:
    g = S.scan('x', Path(p))
    D = g['deaths']
    print(p[-17:], 'death sample', D[:1])
    for d in D:
        if isinstance(d, dict) and d.get('r', 999) <= 110:
            print('  ', d)
    t = [t for t in g['turns'] if t['side'] == 0 and t['r'] in (15, 16)]
    for x in t[:3]:
        print('  turn', x)

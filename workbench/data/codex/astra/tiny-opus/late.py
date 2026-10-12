"""Starter traces r40-100 every 3 rounds with length, online games: python3 -B data/codex/astra/tiny-opus/late.py <game json> ..."""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'data/codex/astra/early-opus')
from pathlib import Path
import scan as S
for p in sys.argv[1:]:
    g = S.scan('x', Path(p))
    print('==', p[-17:], 'our eats', [(e['r'], tuple(e['xy'])) for e in g['eats'] if e['side'] == 0][:8])
    print('   their eats r<=60', [(e['r'], tuple(e['xy'])) for e in g['eats'] if e['side'] == 1 and e['r'] <= 60][:14])
    ids = sorted({t['id'] for t in g['turns'] if t['side'] == 0 and t['r'] <= 1})
    for i in ids[:3]:
        tr = [t for t in g['turns'] if t['id'] == i and 40 <= t['r'] <= 100]
        print('   id', i, ' '.join('%d:%d,%d/L%d%s' % (t['r'], t['h'][0], t['h'][1], t['L'], '' if t['moves'] else '=') for t in tr[::3]))
    for d in g['deaths']:
        if d['side'] == 0 and d['r'] <= 100:
            print('   death', d['r'], d['id'], d['cause'], d['L'], d['h'])

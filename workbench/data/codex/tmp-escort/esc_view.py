"""esc_view.py <arm> <game> <from round> <to round> : the queen's turns in that span (from esc-<arm>.jsonl): her tile and length,
free neighbour tiles, mates within 7 tiles (id, length, tile, tiles away), enemy heads within 3 steps, and head-ons of those rounds."""
import sys
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
arm, game, lo, hi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
for line in (HERE / ('esc-%s.jsonl' % arm)).read_text().splitlines():
    g = json.loads(line)
    if g['game'] != game:
        continue
    w = g['w']
    xy = lambda c: '(%d,%d)' % (c % w, c // w)
    print(game, '%dx%d' % (w, g['h']), 'queen', g['queen'][0], 'fate', g['fate'])
    for t in g['qturns']:
        if lo <= t['r'] <= hi:
            print('r%d queen %s L%d free %d | mates %s | pursuers %s' % (
                t['r'], xy(t['head']), t['L'], t['free'],
                ' '.join('#%d L%d %s d%d' % (m[0], m[1], xy(m[2]), m[3]) for m in sorted(t['mates'], key=lambda m: m[3])),
                ' '.join('#%d L%d %s' % (p[0], p[1], xy(p[2])) for p in t['pur'])))
    for d in g['deaths']:
        if lo <= d['r'] <= hi:
            print('  %s r%d:' % ('head-on' if d['reason'] == 3 else 'death reason %d' % d['reason'], d['r']) + ' #%d (%s, L%d) at %s, mover #%d, %d tiles from our queen' % (
                d['id'], 'ours' if d['s'] == 0 else 'theirs', d['L'], xy(d['head']), d['mover'], d['dq']))
            continue
            print('  head-on r%d: #%d (%s, L%d) at %s, mover #%d, %d tiles from our queen' % (
                d['r'], d['id'], 'ours' if d['s'] == 0 else 'theirs', d['L'], xy(d['head']), d['mover'], d['dq']))

# Scratch (sweep brief): is the within-layout sign of dither/keeps/hot against pearls an effect of crowding?
# Holds our dragon-turns in r0-100 (a count of how many dragons we had) fixed. z-scored inside each layout. No replay opened.
import json
import math
from collections import defaultdict

games = defaultdict(dict)
with open('data/analysis/ladder/dossier/per-game.jsonl') as f:
    for line in f:
        r = json.loads(line)
        games[r['game']][r['relation']] = (r['layout_key'], {k: {q: r['ranges'][k].get(q) for q in (
            'pearls_eaten', 'turns', 'dither', 'no_view_pearl_moved', 'keeps', 'keeps_eligible', 'hot_turns')} for k in ('0-50', '0-100')})
lay = defaultdict(list)
for g in games.values():
    if 'us' in g and 'them' in g:
        lay[g['us'][0]].append(g)

def pear(xs, ys):
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    a = sum((x - mx) ** 2 for x in xs); b = sum((y - my) ** 2 for y in ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(a * b) if a > 0 and b > 0 else float('nan')

def corr3(fx, fy, fc, skip=()):
    cols = ([], [], [])
    for L, gs in lay.items():
        if L in skip:
            continue
        pts = [t for t in ((fx(g), fy(g), fc(g)) for g in gs) if None not in t]
        if len(pts) < 5:
            continue
        for i in range(3):
            m = sum(p[i] for p in pts) / len(pts)
            s = math.sqrt(sum((p[i] - m) ** 2 for p in pts) / len(pts)) or 1.0
            cols[i].extend((p[i] - m) / s for p in pts)
    rxy, rxc, ryc = pear(cols[0], cols[1]), pear(cols[0], cols[2]), pear(cols[1], cols[2])
    part = (rxy - rxc * ryc) / math.sqrt(max(1e-12, (1 - rxc ** 2) * (1 - ryc ** 2)))
    return rxy, part, rxc, len(cols[0])

def ratio(rng, num, den, floor=10):
    def f(g):
        r = g['us'][1][rng]
        return r[num] / r[den] if (r[den] or 0) >= floor else None
    return f
def pearls(g):
    return g['us'][1]['0-100']['pearls_eaten']
def pshare(g):
    a, b = g['us'][1]['0-100']['pearls_eaten'], g['them'][1]['0-100']['pearls_eaten']
    return a / (a + b) if a + b >= 10 else None
def per_turn(g):
    r = g['us'][1]['0-100']
    return r['pearls_eaten'] / r['turns'] if r['turns'] >= 50 else None
def turns(g):
    return g['us'][1]['0-100']['turns']
def turn_share(g):
    a, b = g['us'][1]['0-100']['turns'], g['them'][1]['0-100']['turns']
    return a / (a + b) if a + b else None

X = {'our dither 0-100': ratio('0-100', 'dither', 'no_view_pearl_moved'), 'our dither 0-50': ratio('0-50', 'dither', 'no_view_pearl_moved'),
     'our keeps 0-100': ratio('0-100', 'keeps', 'keeps_eligible'), 'our hot 0-100': ratio('0-100', 'hot_turns', 'turns'),
     'our hot 0-50': ratio('0-50', 'hot_turns', 'turns')}
TD = ('Tower Defense #1',)
for xn, fx in X.items():
    for yn, fy, fc, cn in (('our pearls 0-100', pearls, turns, 'our dragon-turns'), ('pearl share 0-100', pshare, turn_share, 'our share of dragon-turns'),
                           ('our pearls per turn 0-100', per_turn, turns, 'our dragon-turns')):
        a = corr3(fx, fy, fc); b = corr3(fx, fy, fc, skip=TD)
        print('%-17s vs %-26s plain %+.2f, with %s held %+.2f (measure vs control %+.2f, N=%d); without TD %+.2f / %+.2f' % (
            xn, yn, a[0], cn, a[1], a[2], a[3], b[0], b[1]))

# Counts for F14 (run 20261007-0300) from the h3r-shard files (own extraction, h3_reach.py).
import json
from collections import defaultdict
D = 'data/analysis/ladder/'
rows = [json.loads(l) for l in open(D + 'rows.jsonl') if l.strip()]
maps = json.loads(open(D + 'maps.json').read())
X = dict()
for k in range(4):
    for l in open(D + 'work/h3r-shard%d.jsonl' % k):
        g = json.loads(l)
        X[g['game']] = g
print('games', len(X), 'errors', sum(1 for g in X.values() if 'error' in g))
def band(r):
    e = r['opponent_rating']
    return 'a' if e < 1700 else 'b' if e < 1900 else 'c' if e < 2100 else 'd'
SPLIT = '2026-10-06T14:48:15'
main = [r for r in rows if r['our_code'] == 'main' and r['game'] in X]
v31 = [r for r in rows if r['our_code'] == 'v31' and r['game'] in X]
BIG = [k for k in maps if maps[k]['open_tiles'] >= 2000]
SC = ('Tower Defense #1', 'Stripes #1', 'Trauma #1', 'Queen Of Spades #1')
def cls(u, t):
    if u <= 1 and t <= 1: return 'near both'
    if u >= 2 and t >= 2: return 'far both'
    if u <= 1: return 'near us only'
    return 'near them only'
def show(name, g, bal=1, window=None):
    c = defaultdict(lambda: [0, 0, 0])
    c2 = defaultdict(lambda: [0, 0, 0])
    for r in g:
        for u, t, b, w, eu, et, ne in X[r['game']]['table']:
            if bal is not None and b != bal: continue
            if window is not None and w != window: continue
            k = cls(u, t)
            c[k][0] += eu; c[k][1] += et; c[k][2] += ne
            if u == 3 and t == 3:
                c2['13+ from both'][0] += eu; c2['13+ from both'][1] += et
            if u == 2 and t == 2:
                c2['7-12 from both'][0] += eu; c2['7-12 from both'][1] += et
    out = []
    for k in ('near both', 'far both', 'near us only', 'near them only'):
        a, b2, n = c[k]
        out.append('%s: us %d them %d share %.3f (not eaten %d)' % (k, a, b2, a / max(1, a + b2), n))
    for k in ('7-12 from both', '13+ from both'):
        a, b2, n = c2[k]
        out.append('%s: us %d them %d share %.3f' % (k, a, b2, a / max(1, a + b2)))
    print(name, 'games', len(g), '|', ' | '.join(out))
for code, g0 in (('main', main), ('v31', v31)):
    show(code + ' balanced moments', g0)
    show(code + ' all moments', g0, bal=None)
    for b in 'bcd':
        show(code + ' band ' + b + ' balanced', [r for r in g0 if band(r) == b])
    show(code + ' large layouts balanced', [r for r in g0 if r['map_key'] in BIG])
    show(code + ' scarce 2-start layouts balanced', [r for r in g0 if r['map_key'] in SC])
    show(code + ' other layouts balanced', [r for r in g0 if r['map_key'] not in BIG and r['map_key'] not in SC])
    for w, lab in ((0, 'r0-100'), (1, 'r101-300'), (2, 'r301+')):
        show(code + ' balanced ' + lab, g0, window=w)
show('main half1 balanced', [r for r in main if r['time'] < SPLIT])
show('main half2 balanced', [r for r in main if r['time'] >= SPLIT])
# per layout, far both, balanced
for code, g0 in (('main', main), ('v31', v31)):
    out = []
    for k in sorted(maps):
        a = b2 = na = nb = 0
        for r in g0:
            if r['map_key'] != k: continue
            for u, t, b, w, eu, et, ne in X[r['game']]['table']:
                if b != 1: continue
                if u >= 2 and t >= 2:
                    a += eu; b2 += et
                if u <= 1 and t <= 1:
                    na += eu; nb += et
        if a + b2 >= 200:
            out.append((round(a / (a + b2), 2), k, a + b2, round(na / max(1, na + nb), 2)))
    print(code, 'per layout, far-both share (balanced; 200+ pearls) [share, layout, pearls, near-both share]:', sorted(out))

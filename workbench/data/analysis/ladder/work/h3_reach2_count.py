# Counts for F16 (run 20261007-0300) from the h3s-shard files (own extraction, h3_reach2.py).
# Births = natural pearls born, whatever happened to them later. "theirs only" = born within 6 tiles of an opponent head and 7+ from every head of ours.
import json
from collections import defaultdict
D = 'data/analysis/ladder/'
rows = [json.loads(l) for l in open(D + 'rows.jsonl') if l.strip()]
maps = json.loads(open(D + 'maps.json').read())
X = dict()
for k in range(4):
    for l in open(D + 'work/h3s-shard%d.jsonl' % k):
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
def tally(g, bal=2, fast=None, window=None):
    c = defaultdict(int)
    e = defaultdict(lambda: [0, 0])
    for r in g:
        for u, t, b, w, f, eu, et, ne in X[r['game']]['table']:
            if b != bal: continue
            if fast is not None and f != fast: continue
            if window is not None and w != window: continue
            k = 'both' if (u <= 1 and t <= 1) else 'neither' if (u >= 2 and t >= 2) else 'ours only' if u <= 1 else 'theirs only'
            c[k] += eu + et + ne
            e[k][0] += eu; e[k][1] += et
    return c, e
def show(name, g, **kw):
    c, e = tally(g, **kw)
    print(name, 'games', len(g), '| births near ours only', c['ours only'], 'theirs only', c['theirs only'], 'ratio', round(c['theirs only'] / max(1, c['ours only']), 2),
          '| near both', c['both'], 'our share of those eaten', round(e['both'][0] / max(1, sum(e['both'])), 3), '| near neither', c['neither'], 'our share', round(e['neither'][0] / max(1, sum(e['neither'])), 3))
for code, g0 in (('main', main), ('v31', v31)):
    show(code + ' tight balance', g0)
    for b in 'bcd':
        show(code + ' band ' + b, [r for r in g0 if band(r) == b])
    show(code + ' fast respawns', g0, fast=1)
    show(code + ' other births', g0, fast=0)
    for b in 'bc':
        show(code + ' band ' + b + ' fast respawns', [r for r in g0 if band(r) == b], fast=1)
        show(code + ' band ' + b + ' other births', [r for r in g0 if band(r) == b], fast=0)
    for w, lab in ((0, 'r0-100'), (1, 'r101-300'), (2, 'r301+')):
        show(code + ' ' + lab, g0, window=w)
    show(code + ' large layouts', [r for r in g0 if r['map_key'] in BIG])
    show(code + ' other layouts', [r for r in g0 if r['map_key'] not in BIG])
    show(code + ' wins', [r for r in g0 if r['win']])
    show(code + ' losses', [r for r in g0 if not r['win']])
    show(code + ' loose balance only (1.1 to 1.5 times)', g0, bal=1)
show('main half1', [r for r in main if r['time'] < SPLIT])
show('main half2', [r for r in main if r['time'] >= SPLIT])
for code, g0 in (('main', main), ('v31', v31)):
    out = []
    for k in sorted(maps):
        c, e = tally([r for r in g0 if r['map_key'] == k])
        if c['ours only'] + c['theirs only'] >= 300:
            out.append((round(c['theirs only'] / max(1, c['ours only']), 2), k, c['ours only'] + c['theirs only']))
    print(code, 'per layout ratio theirs only / ours only (tight balance, 300+ births):', sorted(out))
    opp = defaultdict(list)
    for r in g0: opp[r['opponent_id']].append(r)
    rr = []
    for o, g in opp.items():
        c, e = tally(g)
        if len(g) >= 5 and c['ours only'] >= 100:
            rr.append(round(c['theirs only'] / c['ours only'], 2))
    print(code, 'per opponent (5+ games, 100+ births near ours only): ratio above 1 for', sum(1 for x in rr if x > 1), 'of', len(rr), 'median', sorted(rr)[len(rr) // 2] if rr else None)

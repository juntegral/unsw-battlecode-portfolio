# Counts for run 20261007-0300 from rows.jsonl and the h3-shard files (own extraction, see h3_extract.py).
import sys, json
from collections import Counter, defaultdict
from statistics import median
D = 'data/analysis/ladder/'
rows = [json.loads(l) for l in open(D + 'rows.jsonl') if l.strip()]
maps = json.loads(open(D + 'maps.json').read())
X = dict()
for k in range(4):
    for l in open(D + 'work/h3-shard%d.jsonl' % k):
        g = json.loads(l)
        X[g['game']] = g
errs = [g for g in X.values() if 'error' in g]
print('extracted', len(X), 'errors', len(errs), errs[:3])
SPLIT = '2026-10-06T14:48:15'
NEW = (1262921, 1263705, 1265766)
def band(r):
    e = r['opponent_rating']
    return 'a' if e < 1700 else 'b' if e < 1900 else 'c' if e < 2100 else 'd'
main = [r for r in rows if r['our_code'] == 'main']
v31 = [r for r in rows if r['our_code'] == 'v31']
bad = [r['game'] for r in main + v31 if len(X[r['game']]['meetings']) != r['head_on']['count']]
print('meeting count differs from rows in', len(bad), 'games')
SL = [('main all', main), ('main band b', [r for r in main if band(r) == 'b']), ('main band c', [r for r in main if band(r) == 'c']),
      ('main band d', [r for r in main if band(r) == 'd']), ('main half1', [r for r in main if r['time'] < SPLIT]),
      ('main half2', [r for r in main if r['time'] >= SPLIT]), ('main new15', [r for r in main if r['battle'] in NEW]),
      ('main wins', [r for r in main if r['win']]), ('main losses', [r for r in main if not r['win']]),
      ('v31 all', v31), ('v31 band b', [r for r in v31 if band(r) == 'b']), ('v31 band c', [r for r in v31 if band(r) == 'c']), ('v31 band d', [r for r in v31 if band(r) == 'd'])]
def meets(g):
    return [m for r in g for m in X[r['game']]['meetings']]
print()
print('F8 / F8b: head-on meetings. row = [round, mover side, mover length, victim length, mover is queen, victim is queen, alive us, alive them, near us, near them]')
for name, g in SL:
    ms = meets(g)
    t = [m for m in ms if m[1] == 't']
    u = [m for m in ms if m[1] == 'u']
    lost_us = sum(m[3] for m in t) + sum(m[2] for m in u)
    lost_them = sum(m[2] for m in t) + sum(m[3] for m in u)
    longer = sum(1 for m in t if m[3] > m[2]); same = sum(1 for m in t if m[3] == m[2])
    ulonger = sum(1 for m in u if m[3] > m[2]); usame = sum(1 for m in u if m[3] == m[2])
    print(name, 'games', len(g), 'meetings', len(ms), 'per game', round(len(ms) / max(1, len(g)), 1), '| their mover share', round(len(t) / max(1, len(ms)), 3),
          '| length lost us', lost_us, 'them', lost_them, 'ratio', round(lost_us / max(1, lost_them), 3),
          '| they ram: our victim longer', round(longer / max(1, len(t)), 3), 'same', round(same / max(1, len(t)), 3),
          '| we ram: their victim longer', round(ulonger / max(1, len(u)), 3), 'same', round(usame / max(1, len(u)), 3))
ms = meets(main)
t = [m for m in ms if m[1] == 't']; u = [m for m in ms if m[1] == 'u']
print('main: their mover lengths', Counter(min(m[2], 9) for m in t).most_common(), 'our victim lengths', Counter(min(m[3], 9) for m in t).most_common())
print('main: our mover lengths', Counter(min(m[2], 9) for m in u).most_common(), 'their victim lengths', Counter(min(m[3], 9) for m in u).most_common())
print('main: mean near heads within 5 of the victim (other than the two): they ram: theirs', round(sum(m[9] for m in t) / len(t), 2), 'ours', round(sum(m[8] for m in t) / len(t), 2),
      '| we ram: ours', round(sum(m[8] for m in u) / len(u), 2), 'theirs', round(sum(m[9] for m in u) / len(u), 2))
print('main: they ram with no friend within 5:', round(sum(1 for m in t if m[9] == 0) / len(t), 3), 'we ram with no friend within 5:', round(sum(1 for m in u if m[8] == 0) / len(u), 3))
for lab, lo, hi in (('r0-100', 0, 100), ('r101-300', 101, 300), ('r301+', 301, 600)):
    w = [m for m in ms if lo <= m[0] <= hi]
    print('main', lab, 'meetings', len(w), 'their mover share', round(sum(1 for m in w if m[1] == 't') / max(1, len(w)), 3))
for lab, f in (('we have 1.5x dragons', lambda m: m[6] >= 1.5 * m[7]), ('similar', lambda m: m[6] < 1.5 * m[7] and m[7] < 1.5 * m[6]), ('they have 1.5x', lambda m: m[7] >= 1.5 * m[6])):
    w = [m for m in ms if f(m)]
    print('main, dragons alive at the meeting:', lab, 'meetings', len(w), 'their mover share', round(sum(1 for m in w if m[1] == 't') / max(1, len(w)), 3))
opp = defaultdict(list)
for r in main:
    opp[r['opponent_id']].append(r)
oo = [(o, g) for o, g in opp.items() if len(g) >= 5]
sh = []
for o, g in oo:
    w = meets(g)
    if w:
        sh.append((round(sum(1 for m in w if m[1] == 't') / len(w), 2), len(w), len(g), g[0]['opponent_rating']))
print('per opponent (5+ main games): their mover share above 0.5 for', sum(1 for s in sh if s[0] > 0.5), 'of', len(sh), sorted(sh))
lay = defaultdict(list)
for r in main:
    lay[r['map_key']].append(r)
sh = []
for k, g in lay.items():
    w = meets(g)
    if len(w) >= 30:
        sh.append((round(sum(1 for m in w if m[1] == 't') / len(w), 2), len(w), k))
print('per layout (30+ meetings):', sorted(sh))
# per game: mover share vs result
pg = []
for r in main:
    w = X[r['game']]['meetings']
    if len(w) >= 10:
        pg.append((sum(1 for m in w if m[1] == 't') / len(w), r['win']))
print('main games with 10+ meetings', len(pg), ': their mover share >= 0.6 ->', sum(1 for a, b in pg if a >= 0.6), 'games, won', sum(b for a, b in pg if a >= 0.6), '; under 0.5 ->', sum(1 for a, b in pg if a < 0.5), 'games, won', sum(b for a, b in pg if a < 0.5))
# queen in meetings
print('main: meetings where the victim is a queen: they ram ours', sum(1 for m in t if m[5]), 'we ram theirs', sum(1 for m in u if m[5]), '| rammer lengths vs our queen', Counter(m[2] for m in t if m[5]).most_common(5), 'vs their queen', Counter(m[2] for m in u if m[5]).most_common(5))

print()
print('NO ACTION deaths, ours. row = [round, length, gap to head of our longest other dragon, its length, it is the queen, our dragons alive, the dead one is the queen]')
for name, g in (('main', main), ('v31', v31)):
    na = [n for r in g for n in X[r['game']]['noact']]
    near = sum(1 for n in na if n[2] is not None and n[2] <= 3)
    print(name, 'deaths', len(na), 'games', len(g), '| within 3 of longest other head', near, round(near / max(1, len(na)), 3), '| within 6', round(sum(1 for n in na if n[2] is not None and n[2] <= 6) / max(1, len(na)), 3),
          '| before r300', sum(1 for n in na if n[0] < 300), round(sum(1 for n in na if n[0] < 300) / max(1, len(na)), 3), '| r0-100', sum(1 for n in na if n[0] <= 100),
          '| dead one is queen', sum(1 for n in na if n[6]), '| lengths', Counter(min(n[1], 6) for n in na).most_common(6))
    print('   gap distribution', Counter(min(n[2], 12) if n[2] is not None else -1 for n in na).most_common(14))
    early = [n for n in na if n[0] < 300]
    print('   before r300: within 3', sum(1 for n in early if n[2] is not None and n[2] <= 3), 'of', len(early), '| rounds', Counter(n[0] // 50 * 50 for n in early).most_common(8))
    late = [n for n in na if n[0] >= 300]
    print('   from r300: within 3', sum(1 for n in late if n[2] is not None and n[2] <= 3), 'of', len(late))

print()
print('F4b splits: round of 5th split (500 if never), ours minus theirs, per game')
def nth(g, s, n):
    v = X[g]['splits'][s]
    return v[n - 1] if len(v) >= n else 500
for name, g in SL:
    if not g: continue
    d5 = [nth(r['game'], 'us', 5) - nth(r['game'], 'them', 5) for r in g]
    d10 = [nth(r['game'], 'us', 10) - nth(r['game'], 'them', 10) for r in g]
    print(name, 'games', len(g), '| 1st split us', median([nth(r['game'], 'us', 1) for r in g]), 'them', median([nth(r['game'], 'them', 1) for r in g]),
          '| 5th us', median([nth(r['game'], 'us', 5) for r in g]), 'them', median([nth(r['game'], 'them', 5) for r in g]), 'diff median', median(d5), 'we later in', sum(1 for x in d5 if x > 0), 'earlier in', sum(1 for x in d5 if x < 0),
          '| 10th us', median([nth(r['game'], 'us', 10) for r in g]), 'them', median([nth(r['game'], 'them', 10) for r in g]), 'diff median', median(d10),
          '| length at split (first 10) us', median([x for r in g for x in X[r['game']]['split_len']['us'][:10]] or [0]), 'them', median([x for r in g for x in X[r['game']]['split_len']['them'][:10]] or [0]))
# same-layout check for F4b on v31: per layout median diff, band d vs band b
print('v31 per layout, median of (our 5th split round - their 5th): band b / band c / band d (games)')
for k in sorted(maps):
    out = []
    for b in 'bcd':
        g = [r for r in v31 if r['map_key'] == k and band(r) == b]
        out.append('%s (%d)' % (median([nth(r['game'], 'us', 5) - nth(r['game'], 'them', 5) for r in g]) if g else '-', len(g)))
    print('  ', k, ' / '.join(out))

print()
print('F7 path: median over games of the per-game median path steps from nearest head to nearest pearl, raw rounds 0-50')
for code, g0 in (('main', main), ('v31', v31), ('main new15', [r for r in main if r['battle'] in NEW])):
    for k in sorted(maps):
        if maps[k]['dragons_at_spawn'] != 2: continue
        g = [r for r in g0 if r['map_key'] == k and X[r['game']].get('path') and X[r['game']]['path']['us']['median'] is not None and X[r['game']]['path']['them']['median'] is not None]
        if not g: continue
        pu = [X[r['game']]['path']['us']['median'] for r in g]; pt = [X[r['game']]['path']['them']['median'] for r in g]
        stall = sum(1 for r in g if r['curves']['100'] and r['curves']['100']['us']['alive'] <= 6 and r['curves']['100']['them']['alive'] >= 15)
        e50u = median([r['curves']['50']['us']['pearls'] for r in g if r['curves']['50']]); e50t = median([r['curves']['50']['them']['pearls'] for r in g if r['curves']['50']])
        print('  ', code, k, 'games', len(g), 'path us', median(pu), 'them', median(pt), '| games where ours >= 2x theirs', sum(1 for a, b in zip(pu, pt) if a >= 2 * b and a > 0), '| pearls by r50 us', e50u, 'them', e50t, '| stalls', stall, 'wins', sum(r['win'] for r in g))

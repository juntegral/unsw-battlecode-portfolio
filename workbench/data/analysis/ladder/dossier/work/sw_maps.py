# Scratch (sweep brief): hot-tile gap by layout against the layout's known fast-tile supply (maps.json). No replay opened.
import json
import math
from collections import defaultdict

maps = json.loads(open('data/analysis/ladder/maps.json').read())
lay = defaultdict(lambda: {'n': 0, 'us': defaultdict(int), 'them': defaultdict(int)})
with open('data/analysis/ladder/dossier/per-game.jsonl') as f:
    for line in f:
        r = json.loads(line)
        d = lay[r['layout_key']]
        d['n'] += 1
        for rng in ('0-100', '101-300'):
            rr = r['ranges'][rng]
            for k in ('hot_turns', 'turns', 'pearls_eaten', 'dither', 'no_view_pearl_moved'):
                d[r['relation']][rng + k] += rr[k] or 0
rows = []
print('layout | games | pearl tiles | fast tiles | fast supply share | method | hot r0-100 ours/theirs | hot r101-300 ours/theirs | pearl share r0-100 | r101-300')
for L in sorted(lay):
    m = maps.get(L, {})
    d = lay[L]
    def sh(side, rng):
        return 100.0 * d[side][rng + 'hot_turns'] / max(1, d[side][rng + 'turns'])
    def ps(rng):
        a, b = d['us'][rng + 'pearls_eaten'], d['them'][rng + 'pearls_eaten']
        return a / max(1, a + b)
    fs = m.get('fast_supply_share')
    rows.append((L, fs, sh('us', '0-100') - sh('them', '0-100'), sh('us', '101-300') - sh('them', '101-300'), ps('0-100'), ps('101-300'), m.get('fast_tiles')))
    print('%-22s %3d %5s %5s %6s %-16s %5.1f/%5.1f %5.1f/%5.1f %.3f %.3f' % (
        L, d['n'] // 2, m.get('pearl_tiles'), m.get('fast_tiles'), ('%.2f' % fs) if isinstance(fs, (int, float)) else str(fs),
        str(m.get('supply_method'))[:16], sh('us', '0-100'), sh('them', '0-100'), sh('us', '101-300'), sh('them', '101-300'), ps('0-100'), ps('101-300')))

def pear(xs, ys):
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    a = sum((x - mx) ** 2 for x in xs); b = sum((y - my) ** 2 for y in ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(a * b) if a > 0 and b > 0 else float('nan')
def rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v)
    for pos, i in enumerate(o):
        r[i] = float(pos)
    return r
known = [t for t in rows if isinstance(t[1], (int, float))]
print('layouts with a fast supply share:', len(known))
for name, idx in (('hot gap r0-100', 2), ('hot gap r101-300', 3), ('pearl share r0-100', 4), ('pearl share r101-300', 5)):
    print('rank correlation across layouts, fast supply share against', name, '%+.2f' % pear(rank([t[1] for t in known]), rank([t[idx] for t in known])))
some = [t for t in known if (t[6] or 0) > 0]; none = [t for t in known if not (t[6] or 0)]
for name, grp in (('layouts with fast tiles', some), ('layouts with none', none)):
    if grp:
        print(name, len(grp), 'mean hot gap r0-100 %+.1f, r101-300 %+.1f, pearl share r0-100 %.3f, r101-300 %.3f' % (
            sum(t[2] for t in grp) / len(grp), sum(t[3] for t in grp) / len(grp), sum(t[4] for t in grp) / len(grp), sum(t[5] for t in grp) / len(grp)))

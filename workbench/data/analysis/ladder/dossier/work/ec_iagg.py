# Scratch (diag-economy): tables from ec_idle-*.jsonl. Dragons of length 2 and 3, rounds 0-300, layout means.
# Usage: python3 data/analysis/ladder/dossier/work/ec_iagg.py
import json
from collections import defaultdict

W = 'data/analysis/ladder/dossier/work/'
NAMES = ('0-3', '4-10', '11-25', '26-60', '61+')
acc = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0]))
for f in ('ec_idle-O0.jsonl', 'ec_idle-O1.jsonl', 'ec_idle-R0.jsonl', 'ec_idle-R1.jsonl'):
    for line in open(W + f):
        r = json.loads(line)
        a = acc[(r['who'], r['layout'])]
        for row in r['acc']:
            v = a[tuple(row[:3])]
            for z in range(4):
                v[z] += row[3 + z]
lays = sorted({k[1] for k in acc})


def lay(f):
    out = []
    for who in 'OR':
        xs = [f(acc[(who, l)]) for l in lays]
        xs = [x for x in xs if x is not None]
        out.append(sum(xs) / len(xs))
    return out


def s(a, idle=None, view=None, z=0):
    return sum(v[z] for k, v in a.items() if (idle is None or k[1] == idle) and (view is None or k[2] == view))


print('rounds since last meal or birth | share of turns % | no pearl in view % | pearls per 1,000 such turns | deaths per 1,000 such turns | share of all no-view turns %')
for i, name in enumerate(NAMES):
    sh = lay(lambda a: 100 * s(a, i) / s(a))
    bl = lay(lambda a: 100 * s(a, i, 0) / s(a, i) if s(a, i) else None)
    ea = lay(lambda a: 1000 * s(a, i, None, 1) / s(a, i) if s(a, i) else None)
    de = lay(lambda a: 1000 * s(a, i, None, 2) / s(a, i) if s(a, i) else None)
    bs = lay(lambda a: 100 * s(a, i, 0) / s(a, None, 0))
    hi = sum(1 for l in lays if s(acc[('R', l)], i) / s(acc[('R', l)]) > s(acc[('O', l)], i) / s(acc[('O', l)]))
    print('%-6s | %5.1f %5.1f (R higher on %2d) | %5.1f %5.1f | %6.1f %6.1f | %5.1f %5.1f | %5.1f %5.1f' % (
        name, sh[0], sh[1], hi, bl[0], bl[1], ea[0], ea[1], de[0], de[1], bs[0], bs[1]))
bl = lay(lambda a: 100 * s(a, None, 0) / s(a))
print('all: no pearl in view %.1f %.1f' % (bl[0], bl[1]))
# our turns with rank-1's idle mix and our own no-view rate inside each bucket, and the other way round
mix = []
for l in lays:
    o, r = acc[('O', l)], acc[('R', l)]
    x = sum((s(r, i) / s(r)) * (s(o, i, 0) / s(o, i) if s(o, i) else 0) for i in range(5))
    y = sum((s(o, i) / s(o)) * (s(r, i, 0) / s(r, i) if s(r, i) else 0) for i in range(5))
    mix.append((100 * x, 100 * y))
print("no-view share with rank-1's idle mix and our rate inside each bucket %.1f; with our mix and rank-1's rates %.1f" % (
    sum(m[0] for m in mix) / len(mix), sum(m[1] for m in mix) / len(mix)))

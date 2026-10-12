# Scratch (diag-opening): inside each bot, does an early measure go with what comes later? Values are taken as the
# difference from the layout mean of that bot, pooled over layouts (correlation), followed side only.
# Later things: pearls eaten in rounds 21-60, pearls by round 100, total length at round 100, the result (win 1, loss 0).
# Usage: python3 data/analysis/ladder/dossier/work/op_link.py
import sys, json, math
sys.dont_write_bytecode = True
from collections import defaultdict
from pathlib import Path

OUT = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/'
W = 'data/analysis/ladder/dossier/work/'
FILES = ['op_scan-O0.jsonl', 'op_scan-O1.jsonl', 'op_scan-O2.jsonl', 'op_scan-O3.jsonl',
         'op_scan-R0.jsonl', 'op_scan-R1.jsonl', 'op_scan-R2.jsonl', 'op_scan-R3.jsonl']
FILES2 = ['op_scan2-O0.jsonl', 'op_scan2-O1.jsonl', 'op_scan2-O2.jsonl', 'op_scan2-O3.jsonl',
          'op_scan2-R0.jsonl', 'op_scan2-R1.jsonl', 'op_scan2-R2.jsonl', 'op_scan2-R3.jsonl']


def load(files):
    games = []
    for f in files:
        p = Path(W + f)
        if not p.exists():
            continue
        with open(W + f) as fh:
            for line in fh:
                if line.strip():
                    games.append(json.loads(line))
    return games


def ser(sd, name, r):
    v = sd['series'][name]
    if len(v) <= r or v[r] < 0:
        return None
    return v[r]


def early(g, sd, x):
    e = {}
    for r in (10, 20):
        e['alive%d' % r] = ser(sd, 'alive', r)
        e['eaten%d' % r] = ser(sd, 'eaten', r)
        e['seen%d' % r] = ser(sd, 'seen', r)
        e['front%d' % r] = ser(sd, 'front', r)
        e['meand%d' % r] = ser(sd, 'meand', r)
        e['spread%d' % r] = ser(sd, 'spread', r)
        e['qd%d' % r] = ser(sd, 'qd', r)
        e['splits by %d' % r] = sum(1 for s in sd['splits'] if s[0] <= r) if g['last_round'] >= r else None
    e['first split round'] = sd['splits'][0][0] if sd['splits'] else None
    e['first pearl eaten'] = min([d[2] for d in sd['dragons'] if d[2] is not None], default=None)
    e['view contact round'] = sd['contact']
    e['deaths r0-20 (alive drop)'] = None
    if x is not None:
        xs = x['sides']['u']
        e['path contact (6) round'] = xs['pc6']
        k5 = [k[3] for k in xs['kids'] if len(k) > 3 and k[3] >= 0 and k[0] <= 20]
        e['parent-child apart +5 (splits r0-20)'] = sum(k5) / len(k5) if k5 else None
        v = [sum(z[j] for z in xs['pearls'].values()) for j in range(10)]
        e['rounds to first seen (born r0-60)'] = v[3] / v[2] if v[2] else None
        e['rounds seen to eaten (born r0-60)'] = v[6] / v[4] if v[4] else None
    return e


def late(g, sd):
    o = {}
    a, b = ser(sd, 'eaten', 60), ser(sd, 'eaten', 20)
    o['pearls r21-60'] = a - b if a is not None and b is not None else None
    o['pearls by 100'] = sd['at100']['eaten'] if sd['at100'] else None
    o['length at 100'] = sd['at100']['total'] if sd['at100'] else None
    o['win'] = 1.0 if g['result'] == 'win' else 0.0 if g['result'] == 'loss' else None
    return o


def corr(pairs):
    by = defaultdict(list)
    for lay, a, b in pairs:
        by[lay].append((a, b))
    xs, ys = [], []
    for lay, v in by.items():
        if len(v) < 4:
            continue
        ma = sum(a for a, b in v) / len(v)
        mb = sum(b for a, b in v) / len(v)
        for a, b in v:
            xs.append(a - ma)
            ys.append(b - mb)
    n = len(xs)
    if n < 20:
        return None, n
    sxx = sum(a * a for a in xs)
    syy = sum(b * b for b in ys)
    if sxx <= 0 or syy <= 0:
        return None, n
    return sum(a * b for a, b in zip(xs, ys)) / math.sqrt(sxx * syy), n


def main():
    games = load(FILES)
    extra = {(x['who'], x['game']): x for x in load(FILES2)}
    lines = []
    for who in 'OR':
        rows = []
        for g in games:
            if g['who'] != who:
                continue
            sd = g['sides']['u']
            rows.append((g['layout'], early(g, sd, extra.get((who, g['game']))), late(g, sd)))
        names = sorted({k for r in rows for k in r[1]})
        outs = ('pearls r21-60', 'pearls by 100', 'length at 100', 'win')
        lines.append('')
        lines.append('== %s: correlation inside layouts (n games) ==' % who)
        lines.append('%-40s' % 'early measure' + ''.join('%22s' % o for o in outs))
        for nm in names:
            cells = []
            for o in outs:
                c, n = corr([(lay, e[nm], l[o]) for lay, e, l in rows if e.get(nm) is not None and l.get(o) is not None])
                cells.append('%22s' % ('%+.2f (%d)' % (c, n) if c is not None else '-'))
            lines.append('%-40s' % nm + ''.join(cells))
    body = '\n'.join(lines) + '\n'
    Path(OUT + 'op_link.txt').write_text(body)
    print(body)


main()

# Scratch (diag-economy): the smaller tables of diag-economy.md. Layout means, equal weight, ours then rank-1.
# Usage: python3 data/analysis/ladder/dossier/work/ec_misc.py <net|supply|layouts|strict|corner|trans>
#   net     : pearls eaten, length lost in deaths and the net, per 1,000 turns (from sl_scan-*.jsonl of diag-split)
#   supply  : pearls born per 1,000 followed-side turns by origin and the share the side eats (ec_scan-*.jsonl)
#   layouts : the gap by layout and band; the share on the closed-start layouts and on the big ones (ec_scan)
#   strict  : pearls eaten by takers of the mate-shut class under the survey's own timing line (ec_bot, first run,
#             which has no turn counts) against the exact timing (ec_bot2)
#   corner  : turns with a pearl beside the head and no other free step, per 1,000 turns (ec_alt)
#   trans   : what the dragon has at its next turn, from the situations without a pearl beside the head (ec_scan)
import sys, json
from collections import defaultdict

W = 'data/analysis/ladder/dossier/work/'
EC = ('ec_scan-O0.jsonl', 'ec_scan-O1.jsonl', 'ec_scan-O2.jsonl', 'ec_scan-R0.jsonl', 'ec_scan-R1.jsonl', 'ec_scan-R2.jsonl')


def load_ec():
    acc = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0, 0]))
    sup = defaultdict(lambda: defaultdict(int))
    for f in EC:
        for line in open(W + f):
            r = json.loads(line)
            a = acc[(r['who'], r['layout'])]
            for row in r['acc']:
                if row[0] == 'U':
                    sup[(r['who'], r['layout'])][tuple(row[1:4])] += row[4]
                    continue
                v = a[tuple(row[:-5])]
                for z in range(5):
                    v[z] += row[-5 + z]
    return acc, sup


def net():
    D = defaultdict(lambda: defaultdict(float))
    for s in range(4):
        for line in open(W + 'sl_scan-%d.jsonl' % s):
            r = json.loads(line)
            d = D[(r['tm'], r['layout'])]
            for bd in range(6):
                b = 'a' if bd <= 3 else 'b'
                d['turns' + b] += r['turns'][0][bd]
                d['eat' + b] += sum(r['eats'][0][bd])
                d['lost' + b] += r['lenlost'][0][bd]
                d['deaths' + b] += r['deathsn'][0][bd]
    lays = sorted({k[1] for k in D})
    for name, bs in (('game', 'ab'), ('r0-300', 'a')):
        g = lambda d, x: sum(d[x + b] for b in bs)
        lay = lambda f: [sum(f(D[(w, l)]) for l in lays) / len(lays) for w in 'OR']
        e = lay(lambda d: 1000 * g(d, 'eat') / g(d, 'turns'))
        lo = lay(lambda d: 1000 * g(d, 'lost') / g(d, 'turns'))
        nt = lay(lambda d: 1000 * (g(d, 'eat') - g(d, 'lost')) / g(d, 'turns'))
        de = lay(lambda d: 1000 * g(d, 'deaths') / g(d, 'turns'))
        hi = sum(1 for l in lays if (g(D[('R', l)], 'eat') - g(D[('R', l)], 'lost')) / g(D[('R', l)], 'turns') >
                 (g(D[('O', l)], 'eat') - g(D[('O', l)], 'lost')) / g(D[('O', l)], 'turns'))
        print('%-7s eaten %.1f %.1f | length lost in deaths %.1f %.1f | net %.2f %.2f (rank-1 higher on %d of 19) | deaths %.1f %.1f' % (
            name, e[0], e[1], lo[0], lo[1], nt[0], nt[1], hi, de[0], de[1]))


def supply():
    acc, sup = load_ec()
    lays = sorted({k[1] for k in acc})
    lay = lambda f: [sum(f(w, l) for l in lays) / len(lays) for w in 'OR']
    for bands, nm in (((0, 1, 2), 'game'), ((0, 1), 'r0-300')):
        turns = lambda w, l: sum(v[0] for k, v in acc[(w, l)].items() if k[1] in bands)
        print(nm)
        for kind, kn in ((0, 'natural'), (1, 'own dead'), (2, 'their dead')):
            eats = lambda w, l: sum(v[1 + kind] for k, v in acc[(w, l)].items() if k[1] in bands)
            born = lambda w, l: sum(sup[(w, l)].get(('born', b, kind), 0) for b in bands)
            a = lay(lambda w, l: 1000 * born(w, l) / turns(w, l))
            b = lay(lambda w, l: 1000 * eats(w, l) / turns(w, l))
            c = lay(lambda w, l: 100 * eats(w, l) / max(1, born(w, l)))
            print('  %-10s born per 1,000 turns %6.1f %6.1f | eaten %6.2f %6.2f | share eaten %5.1f%% %5.1f%%' % (kn, a[0], a[1], b[0], b[1], c[0], c[1]))


def layouts():
    acc, sup = load_ec()
    lays = sorted({k[1] for k in acc})
    closed = ('Maze #1', 'Trauma #1', 'Tower Defense #1', 'Stripes #1')
    per = defaultdict(dict)
    for lay in lays:
        c = {}
        for who in 'OR':
            a = acc[(who, lay)]
            T = sum(v[0] for v in a.values())
            d = defaultdict(lambda: [0, 0])
            for k, v in a.items():
                x = d[('G%d' % (0 if k[1] < 2 else 1)) if k[0] == 'G' else 'T%d' % k[1]]
                x[0] += v[0]
                x[1] += v[1] + v[2] + v[3]
            c[who] = (T, d)
        ro = sum(x[1] for x in c['O'][1].values()) / c['O'][0]
        rr = sum(x[1] for x in c['R'][1].values()) / c['R'][0]
        mid = (ro + rr) / 2
        for lab in ('T0', 'T1', 'T2', 'G0', 'G1'):
            xo, xr = c['O'][1][lab], c['R'][1][lab]
            so, sr = xo[0] / c['O'][0], xr[0] / c['R'][0]
            qo = xo[1] / xo[0] if xo[0] else 0
            qr = xr[1] / xr[0] if xr[0] else qo
            per[lay][lab] = 1000 * ((sr - so) * ((qo + qr) / 2 - mid) + (qr - qo) * (so + sr) / 2)
        per[lay]['all'] = 1000 * (rr - ro)
        p = per[lay]
        print('%-22s gap %6.1f | 2-3 long r0-100 %6.1f, r101-300 %6.1f, r301+ %6.1f | 4+ long r0-300 %6.1f, r301+ %6.1f' % (lay, p['all'], p['T0'], p['T1'], p['T2'], p['G0'], p['G1']))
    n = len(lays)
    print('closed starts, 2-3 long, r0-100: %.2f of the gap; all bands: %.2f' % (sum(per[l]['T0'] for l in closed) / n, sum(per[l]['all'] for l in closed) / n))


def strict():
    def tot(prefix, nvals, eat):
        out = {}
        for who in 'OR':
            e = {0: 0, 1: 0}
            for sh in range(3):
                for line in open(W + '%s-%s%d.jsonl' % (prefix, who, sh)):
                    for row in json.loads(line)['acc']:
                        k, v = row[:-nvals], row[-nvals:]
                        if k[0] == 'A' and k[1] <= 1 and k[11] == 0 and k[-1] == 1 and k[4] < 2 and k[6] == 2:
                            e[k[4]] += v[eat]
            out[who] = e
        return out
    a, b = tot('ec_bot', 6, 0), tot('ec_bot2', 7, 1)
    for who in 'OR':
        print(who, 'pearls eaten by takers, shut now and room if mates timed: trapped %d of %d, tight %d of %d (strict timing of exact timing)' % (
            a[who][0], b[who][0], a[who][1], b[who][1]))


def corner():
    acc = defaultdict(lambda: defaultdict(lambda: [0] * 7))
    for who in 'OR':
        for sh in range(3):
            for line in open(W + 'ec_alt-%s%d.jsonl' % (who, sh)):
                r = json.loads(line)
                a = acc[(r['who'], r['layout'])]
                for row in r['acc']:
                    v = a[tuple(row[:-7])]
                    for z in range(7):
                        v[z] += row[-7 + z]
    lays = sorted({k[1] for k in acc})
    for name, f in (('pearl beside the head, no other free step', lambda k: k[6] == -1),
                    ('pearl beside the head, another free step', lambda k: k[6] >= 0)):
        out = []
        for who in 'OR':
            xs = []
            for l in lays:
                a = acc[(who, l)]
                T = sum(v[0] for k, v in a.items() if k[1] < 2)
                xs.append(1000 * sum(v[0] for k, v in a.items() if k[0] == 'A' and k[1] < 2 and k[7] == 0 and f(k)) / T)
            out.append(sum(xs) / len(xs))
        hi = sum(1 for l in lays if sum(v[0] for k, v in acc[('R', l)].items() if k[0] == 'A' and k[1] < 2 and k[7] == 0 and f(k)) / sum(v[0] for k, v in acc[('R', l)].items() if k[1] < 2) >
                 sum(v[0] for k, v in acc[('O', l)].items() if k[0] == 'A' and k[1] < 2 and k[7] == 0 and f(k)) / sum(v[0] for k, v in acc[('O', l)].items() if k[1] < 2))
        print('%s: %.2f %.2f per 1,000 turns (rank-1 higher on %d of 19)' % (name, out[0], out[1], hi))


def trans():
    tr = defaultdict(lambda: defaultdict(int))
    for f in EC:
        for line in open(W + f):
            r = json.loads(line)
            a = tr[(r['who'], r['layout'])]
            for row in r['trans']:
                a[tuple(row[:-1])] += row[-1]
    lays = sorted({k[1] for k in tr})
    # key: ('T', band, L, pd, E, lead, sub..., what it did, pd at its next turn)
    cases = (('pearl 2 steps away, no mate nearer, no enemy as near, before the leader round: a pearl beside the head next turn',
              lambda k: k[3] == 'B' and k[5] == 0 and k[6] == 2 and k[7] == 0 and k[8] == 0, lambda k: k[-1] == 'A' and k[-2] != 1),
             ('pearl 3 steps away, the same: a pearl within 3 steps next turn',
              lambda k: k[3] == 'B' and k[5] == 0 and k[6] == 3 and k[7] == 0 and k[8] == 0, lambda k: k[-1] in 'AB'),
             ('nothing in view, no enemy within 3: a pearl in view next turn',
              lambda k: k[3] == 'N' and k[4] == 0, lambda k: k[-1] in 'ABC'),
             ('pearl 2 steps away, an enemy head as near: eats it this turn',
              lambda k: k[3] == 'B' and k[5] == 0 and k[6] == 2 and k[7] == 0 and k[8] == 1, lambda k: k[-2] == 1))
    for name, sel, hit in cases:
        vals, hi, n = [[], []], 0, 0
        for l in lays:
            row = []
            for who in 'OR':
                a = tr[(who, l)]
                den = sum(v for k, v in a.items() if k[0] == 'T' and k[1] < 2 and sel(k))
                num = sum(v for k, v in a.items() if k[0] == 'T' and k[1] < 2 and sel(k) and hit(k))
                row.append((num, den))
            if row[0][1] >= 30 and row[1][1] >= 30:
                n += 1
                hi += row[1][0] / row[1][1] > row[0][0] / row[0][1]
                vals[0].append(100 * row[0][0] / row[0][1])
                vals[1].append(100 * row[1][0] / row[1][1])
        print('%s: %.1f%% %.1f%% (rank-1 higher on %d of %d)' % (name, sum(vals[0]) / len(vals[0]), sum(vals[1]) / len(vals[1]), hi, n))


dict(net=net, supply=supply, layouts=layouts, strict=strict, corner=corner, trans=trans)[sys.argv[1]]()

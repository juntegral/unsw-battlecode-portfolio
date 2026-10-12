# Scratch (diag-economy): tables from ec_scan-*.jsonl. Shares and rates are formed inside a layout and then
# averaged over the 19 layouts with equal weight. The gap in pearls per 1,000 turns is split per class into
# "frequency" = (share R - share O) x (mean class rate - mean overall rate) and "rate" = (rate R - rate O) x mean
# share, inside each layout (midpoint split, exact), then averaged; the parts sum to the gap.
# Usage: python3 ec_agg.py [cond] [val=eat|nat|own|opp|fwd] [key=v1,v2 ...] dim [dim ...]
#   filters pick the turns that are split by the dims; the other turns are shown as "rest" rows, or dropped when
#   "cond" is given (shares are then of the filtered turns). Dims and filter keys: band L pd E box J lead n56 D
#   kind origin m1 m2 m4 m8 m16 m32 m64 (A turns), d bkind fresh mn en bm9 (B turns), sd cd (S turns).
import sys, json
from collections import defaultdict
from pathlib import Path

W = 'data/analysis/ladder/dossier/work/'
FILES = ('ec_scan-O0.jsonl', 'ec_scan-O1.jsonl', 'ec_scan-O2.jsonl', 'ec_scan-R0.jsonl', 'ec_scan-R1.jsonl', 'ec_scan-R2.jsonl')
BIT = dict(m1=1, m2=2, m4=4, m8=8, m16=16, m32=32, m64=64)


def load():
    acc = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, 0, 0]))
    sup = defaultdict(lambda: defaultdict(int))
    for f in FILES:
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


def fields(k):
    if k[0] == 'G':
        return dict(t='G', band=k[1], L=k[2], D=k[3])
    f = dict(t='T', band=k[1], L=k[2], pd=k[3], E=k[4], box=k[5], J=k[6], lead=k[7], n56=k[8], D=k[-1])
    sub = k[9:-1]
    if f['pd'] == 'A':
        f.update(kind=sub[0], origin=sub[1])
        for name, bit in BIT.items():
            f[name] = (sub[2] // bit) % 2
    elif f['pd'] == 'B':
        f.update(d=sub[0], bkind=sub[1], fresh=sub[2], mn=sub[3], en=sub[4], bm9=sub[5])
    elif f['pd'] == 'S':
        f.update(sd=sub[0], cd=sub[1])
    return f


def value(v, val):
    return v[1] + v[2] + v[3] if val == 'eat' else v[1] if val == 'nat' else v[2] if val == 'own' else v[3] if val == 'opp' else v[4]


def account(acc, classify, val='eat', cond=False):
    lays = sorted({k[1] for k in acc})
    cells = {}
    for (who, lay), a in acc.items():
        c = cells.setdefault((who, lay), defaultdict(lambda: [0, 0, 0]))
        for k, v in a.items():
            lab = classify(fields(k))
            if lab is None:
                if cond:
                    continue
                f = fields(k)
                lab = 'rest: ' + ('4+ long' if f['t'] == 'G' else '2-3 long') + (' r301+' if f['band'] == 2 else ' r0-300')
            x = c[lab]
            x[0] += v[0]
            x[1] += value(v, val)
            x[2] += v[4]
    labs = sorted({lab for c in cells.values() for lab in c})
    res = {lab: [0.0] * 9 for lab in labs}
    tot = [0.0, 0.0]
    for lay in lays:
        o, r = cells[('O', lay)], cells[('R', lay)]
        to, tr = sum(x[0] for x in o.values()), sum(x[0] for x in r.values())
        ro, rr = sum(x[1] for x in o.values()) / to, sum(x[1] for x in r.values()) / tr
        mid = (ro + rr) / 2
        tot[0] += 1000 * ro / len(lays)
        tot[1] += 1000 * rr / len(lays)
        for lab in labs:
            xo, xr = o.get(lab, (0, 0, 0)), r.get(lab, (0, 0, 0))
            so, sr = xo[0] / to, xr[0] / tr
            qo = xo[1] / xo[0] if xo[0] else None
            qr = xr[1] / xr[0] if xr[0] else None
            if qo is None:
                qo = qr if qr is not None else 0.0
            if qr is None:
                qr = qo
            z = res[lab]
            z[0] += 100 * so / len(lays)
            z[1] += 100 * sr / len(lays)
            z[2] += 1000 * xo[1] / to / len(lays)
            z[3] += 1000 * xr[1] / tr / len(lays)
            z[4] += 1000 * (sr - so) * ((qo + qr) / 2 - mid) / len(lays)
            z[5] += 1000 * (qr - qo) * (so + sr) / 2 / len(lays)
            z[6] += int(xr[1] / tr > xo[1] / to)
            z[7] += xo[2] / to / len(lays)
            z[8] += xr[2] / tr / len(lays)
    return labs, res, tot


def show(labs, res, tot):
    print('%-44s %7s %7s | %7s %7s | %7s %7s | %7s %7s %7s | %2s | %6s %6s' % ('class', 'shO%', 'shR%', 'rateO', 'rateR', 'conO', 'conR', 'freq', 'rate', 'sum', 'Rh', 'fwdO', 'fwdR'))
    sf = sr = 0.0
    for lab in labs:
        z = res[lab]
        sf += z[4]
        sr += z[5]
        print('%-44s %7.2f %7.2f | %7.1f %7.1f | %7.2f %7.2f | %+7.2f %+7.2f %+7.2f | %2d | %6.3f %6.3f' % (
            lab[:44], z[0], z[1], 100 * z[2] / z[0] if z[0] else 0, 100 * z[3] / z[1] if z[1] else 0, z[2], z[3], z[4], z[5], z[4] + z[5], z[6],
            100 * z[7] / z[0] if z[0] else 0, 100 * z[8] / z[1] if z[1] else 0))
    print('%-44s %7s %7s | %7.2f %7.2f | %7s %7s | %+7.2f %+7.2f %+7.2f' % ('ALL', '', '', tot[0], tot[1], '', '', sf, sr, sf + sr))


def acct(f):
    # The account of diag-economy.md: dragons of 2 and 3, rounds 0-300, first class that holds.
    if f['t'] != 'T' or f['band'] == 2:
        return None
    if f['pd'] == 'A':
        if f['m4'] or f['m8']:
            return 'a1 pearl beside: pocket rule or portal step'
        if f['m1']:
            return 'a2 pearl beside: enemy head beside it'
        if f['lead'] and f['m32']:
            return 'a3 pearl beside: leader zone'
        if f['m16']:
            return 'a4 pearl beside: its tile cramped, dragon boxed' if f['box'] <= 1 else 'a5 pearl beside: its tile cramped, dragon in the open'
        if f['origin'] == 0:
            return 'a6 pearl beside: it appeared since the last turn'
        if f['J']:
            return 'a7 pearl beside: just split'
        return 'a8 pearl beside: the dragon walked up to it'
    if f['box'] <= 1:
        return 'b1 no pearl beside: boxed in or dead end'
    if f['E']:
        return 'b2 no pearl beside: enemy head within 3'
    if f['J']:
        return 'b3 no pearl beside: just split'
    return dict(B='c1 pearl 2-3 steps away', C='c2 pearl in view, farther', S='c3 none in view, a tile spawns within 3', N='c4 nothing in view')[f['pd']]


def main():
    acc, sup = load()
    if 'account' in sys.argv[1:]:
        val = [a[4:] for a in sys.argv[1:] if a.startswith('val=')]
        labs, res, tot = account(acc, acct, val[0] if val else 'eat', False)
        show(labs, res, tot)
        return
    cond, val, flt, dims = False, 'eat', {}, []
    for a in sys.argv[1:]:
        if a == 'cond':
            cond = True
        elif a.startswith('val='):
            val = a[4:]
        elif '=' in a:
            k, vs = a.split('=')
            flt[k] = set(vs.split(','))
        else:
            dims.append(a)

    def classify(f):
        if f['t'] != 'T':
            return None
        for k, vs in flt.items():
            if k not in f or str(f[k]) not in vs:
                return None
        return ' '.join('%s=%s' % (d, f.get(d, '-')) for d in dims) if dims else 'all'

    labs, res, tot = account(acc, classify, val, cond)
    show(labs, res, tot)


main()

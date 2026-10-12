# Scratch (diag-walk): tables from wk_scan-*.jsonl. Every rate is first formed inside a layout (all games of that bot on
# that layout pooled), then averaged over the 19 shared layouts with equal weight, as the scoreboard does.
# Usage: python3 data/analysis/ladder/dossier/work/wk_agg.py [section ...]
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

WORK = Path('data/analysis/ladder/dossier/work')
WIN = ('r0-100', 'r101-300')
SC = ('T', 'S', 'R', 'H', 'C', 'Nc', 'N4', 'N6', 'Nf')
AR = ('M', 'K', 'P', 'W', 'O')
want = set(sys.argv[1:])


def on(name):
    return not want or name in want


def load():
    recs = dict(O=[], R=[])
    for path in sorted(WORK.glob('wk_scan-[OR][0-9].jsonl')):
        with open(path) as f:
            for line in f:
                r = json.loads(line)
                recs[r['who']].append(r)
    return recs


RECS = load()
LAYOUTS = sorted({r['layout'] for r in RECS['O']}.intersection({r['layout'] for r in RECS['R']}))
print('games', {w: len(v) for w, v in RECS.items()}, 'layouts', len(LAYOUTS))


def table(who, field, size):
    # {layout: {key: summed vector}}
    out = {l: defaultdict(lambda: [0] * size) for l in LAYOUTS}
    for r in RECS[who]:
        t = out.get(r['layout'])
        if t is None:
            continue
        for k, v in r[field].items():
            acc = t[k]
            if isinstance(v, int):
                acc[0] += v
            else:
                for n, x in enumerate(v):
                    acc[n] += x
    return out


def fold(tab, keyfn):
    out = {}
    for l, t in tab.items():
        d = defaultdict(lambda: None)
        for k, v in t.items():
            kk = keyfn(k.split('|'))
            if kk is None:
                continue
            if d[kk] is None:
                d[kk] = list(v)
            else:
                d[kk] = [a + c for a, c in zip(d[kk], v)]
        out[l] = d
    return out


def eq(vals):
    vals = [v for v in vals if v is not None]
    return mean(vals) if vals else None


def ratio(a, c):
    return a / c if c else None


def pct(x, nd=1):
    return 'NA' if x is None else ('%.' + str(nd) + 'f') % (100 * x)


def num(x, nd=2):
    return 'NA' if x is None else ('%.' + str(nd) + 'f') % x


def rate_eq(tab, keyfn, a, c):
    # layout-equal mean of sum_a/sum_c for the keys that keyfn keeps (keyfn returns True/None)
    f = fold(tab, lambda q: 'x' if keyfn(q) else None)
    vals = []
    for l in LAYOUTS:
        v = f[l]['x']
        vals.append(ratio(v[a], v[c]) if v else None)
    return eq(vals), vals


def higher(vo, vr):
    n = sum(1 for a, c in zip(vo, vr) if a is not None and c is not None and c > a)
    m = sum(1 for a, c in zip(vo, vr) if a is not None and c is not None)
    return '%d/%d' % (n, m)


STEPS = {w: table(w, 'steps', 12) for w in 'OR'}


def breakdown(title, wi, keyfn, order=None, base=None):
    # share of blind moved turns, re-tread rate inside the kind, and the kind's part of the total rate; layout-equal
    print('\n' + title + ' ' + WIN[wi])
    print('kind | share O | share R | re-tread O | re-tread R | kept O | kept R | part O | part R | part gap')
    res = {}
    for who in 'OR':
        f = fold(STEPS[who], lambda q: (keyfn(q) if int(q[0]) == wi and (base is None or base(q)) else None))
        kinds = set()
        for l in LAYOUTS:
            kinds.update(f[l].keys())
        res[who] = (f, kinds)
    kinds = sorted(res['O'][1].union(res['R'][1]), key=lambda k: (order.index(k) if order and k in order else 99, str(k)))
    tot = {}
    for who in 'OR':
        f = res[who][0]
        tot[who] = {l: sum(v[0] for v in f[l].values() if v) for l in LAYOUTS}
    gap_sum = 0.0
    for k in kinds:
        cells = []
        for who in 'OR':
            f = res[who][0]
            share = eq([ratio((f[l][k] or [0])[0], tot[who][l]) for l in LAYOUTS])
            part = eq([ratio((f[l][k] or [0, 0])[1], tot[who][l]) for l in LAYOUTS])
            rate = eq([ratio(f[l][k][1], f[l][k][0]) if f[l][k] else None for l in LAYOUTS])
            kept = eq([ratio(f[l][k][3], f[l][k][2]) if f[l][k] else None for l in LAYOUTS])
            cells.append((share, part, rate, kept))
        (so, po, ro, ko), (sr, pr, rr, kr) = cells
        gap = (po or 0) - (pr or 0)
        gap_sum += gap
        print('%s | %s | %s | %s | %s | %s | %s | %s | %s | %+.2f' % (k, pct(so), pct(sr), pct(ro), pct(rr), pct(ko), pct(kr), pct(po, 2), pct(pr, 2), 100 * gap))
    print('sum of part gaps %+.2f' % (100 * gap_sum))


def std_mix(wi, keyfn, label):
    # our mix of kinds with rank-1's re-tread rate inside each kind (layout by layout; a kind rank-1 never has keeps our rate)
    vals_o, vals_r, vals_x = [], [], []
    fo = fold(STEPS['O'], lambda q: keyfn(q) if int(q[0]) == wi else None)
    fr = fold(STEPS['R'], lambda q: keyfn(q) if int(q[0]) == wi else None)
    for l in LAYOUTS:
        to = sum(v[0] for v in fo[l].values() if v)
        tr = sum(v[0] for v in fr[l].values() if v)
        if not to or not tr:
            continue
        vals_o.append(sum(v[1] for v in fo[l].values() if v) / to)
        vals_r.append(sum(v[1] for v in fr[l].values() if v) / tr)
        x = 0.0
        for k, v in fo[l].items():
            if not v:
                continue
            rv = fr[l][k]
            rate = rv[1] / rv[0] if rv and rv[0] >= 20 else v[1] / v[0]
            x += v[0] / to * rate
        vals_x.append(x)
    print('%s %s: ours %s, rank-1 %s, our mix with rank-1 rates inside each kind %s' % (label, WIN[wi], pct(mean(vals_o)), pct(mean(vals_r)), pct(mean(vals_x))))


if on('check'):
    print('\n== check against the scoreboard (layout-equal) ==')
    for wi in (0, 1):
        for who in 'OR':
            bl = defaultdict(lambda: [0, 0])
            for r in RECS[who]:
                c = r['chk'][wi]
                bl[r['layout']][0] += c['turns']
                bl[r['layout']][1] += c['blind']
            blind = eq([ratio(bl[l][1], bl[l][0]) for l in LAYOUTS])
            re, _ = rate_eq(STEPS[who], lambda q: int(q[0]) == wi, 1, 0)
            kp, _ = rate_eq(STEPS[who], lambda q: int(q[0]) == wi, 3, 2)
            print(WIN[wi], who, 'blind turns', pct(blind), 're-tread', pct(re), 'kept', pct(kp))

if on('kinds'):
    for wi in (0, 1):
        breakdown('== by length ==', wi, lambda q: q[1], order=['2', '3', '4', '5', '8'])
        breakdown('== by rounds since birth (a 0-5, b 6-15, c 16-40, d 41+) ==', wi, lambda q: q[2])
        breakdown('== by what can score ==', wi, lambda q: q[3], order=list(SC))
        breakdown('== by what is around ==', wi, lambda q: q[4], order=list(AR))
        breakdown('== nothing scores (N4 N6 Nf) by what is around ==', wi, lambda q: q[4], order=list(AR), base=lambda q: q[3] in ('N4', 'N6', 'Nf'))
        breakdown('== nothing scores, by length ==', wi, lambda q: q[1], order=['2', '3', '4', '5', '8'], base=lambda q: q[3] in ('N4', 'N6', 'Nf'))
        breakdown('== grouped: threat / target (S R H) / cramped / centre / nothing ==', wi,
                  lambda q: dict(T='threat', S='target', R='target', H='target', C='cramped', Nc='centre').get(q[3], 'nothing'),
                  order=['threat', 'target', 'cramped', 'centre', 'nothing'])
        breakdown('== blind for 5+ rounds or not ==', wi, lambda q: 'long' if q[5] == '1' else 'short')
        std_mix(wi, lambda q: (q[1], q[2]), 'length x age')
        std_mix(wi, lambda q: (q[1], q[2], q[3], q[4]), 'length x age x scores x around')
        std_mix(wi, lambda q: (q[3], q[4]), 'scores x around')

if on('detail'):
    print('\n== re-tread steps: how many steps ago the tile was left, and whether there was a choice ==')
    for wi in (0, 1):
        for who in 'OR':
            t = table(who, 'retc', 1)
            for name, idx, keys in (('ago', 3, ('3', '5', '7', '9', 'x')), ('alt', 4, ('forced', 'boxed', 'choice'))):
                f = fold(t, lambda q: q[idx] if int(q[0]) == wi else None)
                row = []
                for k in keys:
                    row.append(k + ' ' + pct(eq([ratio((f[l][k] or [0])[0], sum(v[0] for v in f[l].values() if v)) for l in LAYOUTS])))
                print(WIN[wi], who, name, ' | '.join(row))
            f = fold(t, lambda q: (q[1] + ':' + q[3]) if int(q[0]) == wi else None)
            row = []
            for k in ('2:3', '3:3', '2:5', '3:5', '4:5', '5:5'):
                row.append(k + ' ' + pct(eq([ratio((f[l][k] or [0])[0], sum(v[0] for v in f[l].values() if v)) for l in LAYOUTS])))
            print(WIN[wi], who, 'length:ago share of all re-tread steps', ' | '.join(row))
    print('\n== nothing-scores steps: does the step lie on a shortest way to the nearest never-seen tile ==')
    for wi in (0, 1):
        for who in 'OR':
            t = table(who, 'nc', 1)
            for sc in ('Nc', 'N4', 'N6', 'Nf'):
                f = fold(t, lambda q: (q[2] + q[3] + q[4]) if int(q[0]) == wi and q[1] == sc else None)
                tot = {l: sum(v[0] for v in f[l].values() if v) for l in LAYOUTS}
                def share(test):
                    return eq([ratio(sum(v[0] for k, v in f[l].items() if v and test(k)), tot[l]) for l in LAYOUTS])
                def cond(test, base):
                    return eq([ratio(sum(v[0] for k, v in f[l].items() if v and test(k) and base(k)), sum(v[0] for k, v in f[l].items() if v and base(k))) for l in LAYOUTS])
                print(WIN[wi], who, sc, 'toward unseen: all steps', pct(cond(lambda k: k[1] == '1', lambda k: k[1] != '2')),
                      '| re-tread steps', pct(cond(lambda k: k[1] == '1', lambda k: k[1] != '2' and k[0] == '1')),
                      '| toward centre: all', pct(share(lambda k: k[2] == '1')), 're-tread', pct(cond(lambda k: k[2] == '1', lambda k: k[0] == '1')),
                      '| re-tread rate when toward unseen', pct(cond(lambda k: k[0] == '1', lambda k: k[1] == '1')),
                      'when not', pct(cond(lambda k: k[0] == '1', lambda k: k[1] == '0')))
    print('\n== queen against the rest ==')
    for wi in (0, 1):
        for who in 'OR':
            t = table(who, 'queenc', 4)
            for qn in ('1', '0'):
                f = fold(t, lambda q: 'x' if int(q[0]) == wi and q[1] == qn else None)
                print(WIN[wi], who, 'queen' if qn == '1' else 'others', 're-tread', pct(eq([ratio(f[l]['x'][1], f[l]['x'][0]) if f[l]['x'] else None for l in LAYOUTS])),
                      'kept', pct(eq([ratio(f[l]['x'][3], f[l]['x'][2]) if f[l]['x'] else None for l in LAYOUTS])),
                      'share of blind moved', pct(eq([ratio(f[l]['x'][0] if f[l]['x'] else 0, sum(v[0] for k, v in t[l].items() if int(k.split('|')[0]) == wi)) for l in LAYOUTS])))

if on('worth'):
    print('\n== what a step buys: pearl in view at the next turn start, and pearls eaten in the next 10 rounds ==')
    groups = (('all blind moved', lambda q: True), ('nothing scores (N4 N6 Nf)', lambda q: q[3] in ('N4', 'N6', 'Nf')),
              ('nothing scores, open or walls near', lambda q: q[3] in ('N4', 'N6', 'Nf') and q[4] in ('O', 'W')),
              ('nothing scores, blind 5+ rounds', lambda q: q[3] in ('N4', 'N6', 'Nf') and q[5] == '1'),
              ('Nf only', lambda q: q[3] == 'Nf'), ('target in view (S R H)', lambda q: q[3] in ('S', 'R', 'H')))
    for wi in (0, 1):
        for name, test in groups:
            for who in 'OR':
                fn = lambda q: int(q[0]) == wi and test(q)
                a, va = rate_eq(STEPS[who], fn, 5, 4)
                c, vc = rate_eq(STEPS[who], fn, 7, 6)
                e, ve = rate_eq(STEPS[who], fn, 9, 8)
                f, vf = rate_eq(STEPS[who], fn, 11, 10)
                print(WIN[wi], who, name, '| found next: new tile', pct(a), 're-tread', pct(c), 'new higher on', higher(vc, va),
                      '| eaten in 10 rounds per step: new', num(e, 3), 're-tread', num(f, 3), 'new higher on', higher(vf, ve))

if on('part2'):
    print('\n== part 2, layout by layout ==')
    rows = {}
    for who in 'OR':
        st = table(who, 'streakc', 5)
        bo = table(who, 'born', 1)
        for l in LAYOUTS:
            gs = [r for r in RECS[who] if r['layout'] == l]
            d = {}
            d['seen50'] = eq([r['seen50'] / r['cells'] if r['seen50'] is not None else None for r in gs])
            d['seen100'] = eq([r['seen100'] / r['cells'] if r['seen100'] is not None else None for r in gs])
            d['contact'] = eq([r['first_contact'] for r in gs])
            lg = [0] * 5
            for k, v in st[l].items():
                q = k.split('|')
                if q[1] in ('2', '3'):
                    lg = [a + c for a, c in zip(lg, v)]
            d['long_found'] = ratio(lg[2], lg[1])
            d['long_eat10'] = ratio(lg[4], lg[3])
            d['long_share'] = ratio(lg[0], sum(r['chk'][0]['turns'] + r['chk'][1]['turns'] for r in gs))
            for tag, test in (('kid', lambda q: True), ('kidblind', lambda q: q[1] == '1')):
                for hz in (10, 20):
                    okn = tot = 0
                    for k, v in bo[l].items():
                        q = k.split('|')
                        if not test(q):
                            continue
                        code, val = q[2][0], int(q[2][1:])
                        if code == 'c' and val < hz:
                            continue
                        tot += v[0]
                        okn += v[0] if code == 'f' and val <= hz else 0
                    d['%s_fed%d' % (tag, hz)] = ratio(okn, tot)
                waits = []
                for k, v in bo[l].items():
                    q = k.split('|')
                    if test(q) and q[2][0] == 'f':
                        waits += [int(q[2][1:])] * v[0]
                d[tag + '_wait'] = median(waits) if waits else None
                d[tag + '_n'] = sum(v[0] for k, v in bo[l].items() if test(k.split('|')))
            dead = sum(v[0] for k, v in bo[l].items() if k.split('|')[2][0] == 'd' and int(k.split('|')[2][1:]) <= 20)
            d['kid_dead20'] = ratio(dead, d['kid_n'])
            d['kid_bornblind'] = ratio(d['kidblind_n'], d['kid_n'])
            rows[who, l] = d
    names = ('seen50', 'seen100', 'contact', 'long_share', 'long_found', 'long_eat10', 'kid_bornblind', 'kid_fed10', 'kid_fed20', 'kid_wait',
             'kidblind_fed10', 'kidblind_fed20', 'kidblind_wait', 'kid_dead20')
    print('measure | ours | rank-1 | rank-1 higher on')
    for nme in names:
        vo = [rows['O', l][nme] for l in LAYOUTS]
        vr = [rows['R', l][nme] for l in LAYOUTS]
        print(nme, '|', num(eq(vo), 3), '|', num(eq(vr), 3), '|', higher(vo, vr))
    if 'layouts' in want:
        for l in LAYOUTS:
            print(l, ' '.join('%s %s/%s' % (nme, num(rows['O', l][nme], 3), num(rows['R', l][nme], 3)) for nme in names))

if on('blind'):
    print('\n== where the extra blind turns come from ==')
    for wi in (0, 1):
        ep = {}
        for who in 'OR':
            acc = defaultdict(lambda: [0, 0, 0])
            for r in RECS[who]:
                a = acc[r['layout']]
                a[0] += r['chk'][wi]['turns']
                a[1] += r['chk'][wi]['blind']
                a[2] += r['episodes'][wi]
            ep[who] = acc
            print(WIN[wi], who, 'blind share', pct(eq([ratio(acc[l][1], acc[l][0]) for l in LAYOUTS])),
                  '| blind spells started per 100 turns', num(eq([ratio(100 * acc[l][2], acc[l][0]) for l in LAYOUTS])),
                  '| mean spell length', num(eq([ratio(acc[l][1], acc[l][2]) for l in LAYOUTS])))
        print(WIN[wi], 'rank-1 lower on: spells started', higher([ratio(ep['R'][l][2], ep['R'][l][0]) for l in LAYOUTS], [ratio(ep['O'][l][2], ep['O'][l][0]) for l in LAYOUTS]),
              'spell length', higher([ratio(ep['R'][l][1], ep['R'][l][2]) for l in LAYOUTS], [ratio(ep['O'][l][1], ep['O'][l][2]) for l in LAYOUTS]))
        bt = {who: table(who, 'blindc', 2) for who in 'OR'}
        for name, idx, keys in (('pearls on the board per 1000 tiles (0 <4, 1 4-8, 2 8-16, 3 16-32, 4 32+)', 1, '01234'),
                                ('team mates in view (0, 1, 2+)', 2, '012'), ('a tile with 2+ births in view', 3, '01')):
            print(WIN[wi], name)
            for k in keys:
                cells = []
                for who in 'OR':
                    f = fold(bt[who], lambda q: q[idx] if int(q[0]) == wi else None)
                    tot = {l: sum(v[0] for v in f[l].values() if v) for l in LAYOUTS}
                    cells.append((eq([ratio((f[l][k] or [0])[0], tot[l]) for l in LAYOUTS]),
                                  eq([ratio(f[l][k][1], f[l][k][0]) if f[l][k] else None for l in LAYOUTS])))
                print('  ', k, 'share of turns O', pct(cells[0][0]), 'R', pct(cells[1][0]), '| blind inside O', pct(cells[0][1]), 'R', pct(cells[1][1]))
        for label, keyfn in (('board pearls', lambda q: q[1]), ('board pearls x mates x repeat tile', lambda q: (q[1], q[2], q[3])), ('mates x repeat tile', lambda q: (q[2], q[3]))):
            fo = fold(bt['O'], lambda q: keyfn(q) if int(q[0]) == wi else None)
            fr = fold(bt['R'], lambda q: keyfn(q) if int(q[0]) == wi else None)
            xs, ys = [], []
            for l in LAYOUTS:
                to = sum(v[0] for v in fo[l].values() if v)
                tr = sum(v[0] for v in fr[l].values() if v)
                x = y = 0.0
                for k, v in fo[l].items():
                    if v:
                        rv = fr[l][k]
                        x += v[0] / to * (rv[1] / rv[0] if rv and rv[0] >= 50 else v[1] / v[0])
                for k, v in fr[l].items():
                    if v:
                        ov = fo[l][k]
                        y += v[0] / tr * (ov[1] / ov[0] if ov and ov[0] >= 50 else v[1] / v[0])
                xs.append(x)
                ys.append(y)
            print(WIN[wi], 'standardised on', label, ': our mix with rank-1 blind rates', pct(mean(xs)), '| rank-1 mix with our blind rates', pct(mean(ys)))

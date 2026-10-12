# Scratch (diag-walk): follow-up cuts on wk_scan-*.jsonl: sizes per game, pearls at stake, layout counts per kind,
# the centre-rule kind layout by layout, and where rank-1's long-blind dragons find more.
# Usage: python3 data/analysis/ladder/dossier/work/wk_more.py
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict
from pathlib import Path
from statistics import mean

WORK = Path('data/analysis/ladder/dossier/work')
WIN = ('r0-100', 'r101-300')
NOTH = ('N4', 'N6', 'Nf')
RECS = dict(O=[], R=[])
for path in sorted(WORK.glob('wk_scan-[OR][0-9].jsonl')):
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            RECS[r['who']].append(r)
LAYOUTS = sorted({r['layout'] for r in RECS['O']})


def lay(who, test, idx):
    # {layout: [sum of vector entries idx...]} over step keys passing test
    out = {l: [0] * len(idx) for l in LAYOUTS}
    for r in RECS[who]:
        acc = out[r['layout']]
        for k, v in r['steps'].items():
            q = k.split('|')
            if test(q):
                for n, i in enumerate(idx):
                    acc[n] += v[i]
    return out


def eqrate(tab, a, c):
    vals = [tab[l][a] / tab[l][c] for l in LAYOUTS if tab[l][c]]
    return mean(vals) if vals else None


def lower(to, tr, a, c, least=30):
    n = m = 0
    for l in LAYOUTS:
        if to[l][c] >= least and tr[l][c] >= least:
            m += 1
            n += int(tr[l][a] / tr[l][c] < to[l][a] / to[l][c])
    return '%d/%d' % (n, m)


def p(x, nd=1):
    return 'NA' if x is None else ('%.' + str(nd) + 'f') % (100 * x)


print('== per game, ours and rank-1 (plain means over games) ==')
for who in 'OR':
    for wi in (0, 1):
        gs = RECS[who]
        turns = mean(r['chk'][wi]['turns'] for r in gs)
        moved = mean(r['chk'][wi]['moved'] for r in gs)
        dither = mean(r['chk'][wi]['dither'] for r in gs)
        pearls = mean(r['chk'][wi]['pearls'] for r in gs)
        nn = mean(sum(v[0] for k, v in r['steps'].items() if int(k[0]) == wi and k.split('|')[3] in NOTH) for r in gs)
        nr = mean(sum(v[1] for k, v in r['steps'].items() if int(k[0]) == wi and k.split('|')[3] in NOTH) for r in gs)
        print(who, WIN[wi], 'turns %.0f blind moved %.0f re-tread %.0f pearls eaten %.1f | nothing-scores steps %.0f of them re-tread %.0f' % (turns, moved, dither, pearls, nn, nr))

print('\n== layouts where rank-1 re-treads less / keeps direction more, by kind (layouts with 30+ steps on both sides) ==')
kinds = (('all', lambda q: True), ('threat T', lambda q: q[3] == 'T'), ('target S R H', lambda q: q[3] in ('S', 'R', 'H')),
         ('S pearl due in view', lambda q: q[3] == 'S'), ('R remembered pearl', lambda q: q[3] == 'R'), ('H repeat tile', lambda q: q[3] == 'H'),
         ('centre Nc', lambda q: q[3] == 'Nc'), ('nothing', lambda q: q[3] in NOTH), ('nothing, mate within 3', lambda q: q[3] in NOTH and q[4] == 'M'),
         ('nothing, no mate within 3', lambda q: q[3] in NOTH and q[4] != 'M'), ('nothing, open or walls near', lambda q: q[3] in NOTH and q[4] in ('O', 'W')),
         ('nothing N4', lambda q: q[3] == 'N4'), ('nothing N6 Nf', lambda q: q[3] in ('N6', 'Nf')), ('pocket K', lambda q: q[4] == 'K'), ('cramped C', lambda q: q[3] == 'C'),
         ('length 2', lambda q: q[1] == '2'), ('length 3', lambda q: q[1] == '3'), ('age 41+', lambda q: q[2] == 'd'), ('blind 5+', lambda q: q[5] == '1'))
for wi in (0, 1):
    for name, test in kinds:
        to = lay('O', lambda q: int(q[0]) == wi and test(q), (0, 1, 2, 3))
        tr = lay('R', lambda q: int(q[0]) == wi and test(q), (0, 1, 2, 3))
        print(WIN[wi], name, '| re-tread O', p(eqrate(to, 1, 0)), 'R', p(eqrate(tr, 1, 0)), 'R lower on', lower(to, tr, 1, 0),
              '| kept O', p(eqrate(to, 3, 2)), 'R', p(eqrate(tr, 3, 2)), 'R higher on', lower(tr, to, 3, 2))

print('\n== centre-rule kind (Nc), layout by layout, r0-100: steps, re-tread ==')
to = lay('O', lambda q: q[0] == '0' and q[3] == 'Nc', (0, 1))
tr = lay('R', lambda q: q[0] == '0' and q[3] == 'Nc', (0, 1))
ta = lay('O', lambda q: q[0] == '0', (0, 1))
for l in LAYOUTS:
    if to[l][0]:
        print(l, 'O', to[l][0], p(to[l][1] / to[l][0]), 'share of our blind moved', p(to[l][0] / ta[l][0]), '| R', tr[l][0], p(tr[l][1] / tr[l][0]) if tr[l][0] else 'NA')

print('\n== after any blind moved step: pearl in view next turn, pearls eaten in 10 rounds; by kind (both step types pooled) ==')
cuts = (('all', lambda q: True), ('nothing', lambda q: q[3] in NOTH), ('nothing, mate within 3', lambda q: q[3] in NOTH and q[4] == 'M'),
        ('nothing, open or walls near', lambda q: q[3] in NOTH and q[4] in ('O', 'W')), ('nothing, portal or pocket', lambda q: q[3] in NOTH and q[4] in ('P', 'K')),
        ('target S R H', lambda q: q[3] in ('S', 'R', 'H')), ('threat', lambda q: q[3] == 'T'),
        ('blind 5+', lambda q: q[5] == '1'), ('blind 5+, nothing', lambda q: q[5] == '1' and q[3] in NOTH),
        ('blind 5+, nothing, open or walls near', lambda q: q[5] == '1' and q[3] in NOTH and q[4] in ('O', 'W')),
        ('blind 5+, target', lambda q: q[5] == '1' and q[3] in ('S', 'R', 'H')), ('blind 5+, threat', lambda q: q[5] == '1' and q[3] == 'T'))
for wi in (0, 1):
    for name, test in cuts:
        row = []
        tabs = {}
        for who in 'OR':
            t = lay(who, lambda q: int(q[0]) == wi and test(q), (4, 5, 6, 7, 8, 9, 10, 11, 0))
            t2 = {l: [v[0] + v[2], v[1] + v[3], v[4] + v[6], v[5] + v[7], v[8]] for l, v in t.items()}
            tabs[who] = t2
            row.append('%s found %s eaten10 %.3f' % (who, p(eqrate(t2, 1, 0)), eqrate(t2, 3, 2) or 0))
        tot = {who: lay(who, lambda q: int(q[0]) == wi, (0,)) for who in 'OR'}
        share = {who: mean(tabs[who][l][4] / tot[who][l][0] for l in LAYOUTS if tot[who][l][0]) for who in 'OR'}
        print(WIN[wi], name, '|', ' | '.join(row), '| R higher on: found', lower(tabs['R'], tabs['O'], 1, 0), 'eaten', lower(tabs['R'], tabs['O'], 3, 2),
              '| share of blind moved O', p(share['O']), 'R', p(share['R']))

print('\n== pearls at stake inside our own games (plain sums over our 500 games) ==')
for wi in (0, 1):
    for name, test in (('nothing', lambda q: q[3] in NOTH), ('nothing N6 Nf', lambda q: q[3] in ('N6', 'Nf')), ('centre Nc', lambda q: q[3] == 'Nc'),
                       ('target S R H', lambda q: q[3] in ('S', 'R', 'H')), ('threat', lambda q: q[3] == 'T'), ('all', lambda q: True)):
        v = [0] * 12
        for r in RECS['O']:
            for k, x in r['steps'].items():
                q = k.split('|')
                if int(q[0]) == wi and test(q):
                    v = [a + c for a, c in zip(v, x)]
        vr = [0] * 12
        for r in RECS['R']:
            for k, x in r['steps'].items():
                q = k.split('|')
                if int(q[0]) == wi and test(q):
                    vr = [a + c for a, c in zip(vr, x)]
        new = v[9] / max(1, v[8])
        old = v[11] / max(1, v[10])
        excess = v[1] - v[0] * vr[1] / max(1, vr[0])
        print(WIN[wi], name, 'steps per game %.0f, re-tread %.1f%% (rank-1 pooled %.1f%%), eaten in 10 rounds after a new-tile step %.3f, after a re-tread %.3f, re-tread steps above rank-1 rate per game %.1f, pearls per game if each were a new-tile step %+.2f' % (
            v[0] / 500, 100 * v[1] / max(1, v[0]), 100 * vr[1] / max(1, vr[0]), new, old, excess / 500, excess / 500 * (new - old)))

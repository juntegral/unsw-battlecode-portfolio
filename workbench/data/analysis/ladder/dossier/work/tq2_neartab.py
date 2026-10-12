"""Scratch (diag-topqueen): how each queen moves at each distance from the nearest enemy head. Reads tq2_near-*.jsonl.
Usage: python3 tq2_neartab.py [arm ...]"""
import sys
import json
from collections import Counter, defaultdict
from pathlib import Path

W = Path('data/analysis/ladder/dossier/work')
FILES = ['top3-0', 'top3-1', 't91-0', 't91-1', 't264-0', 't264-1', 't306-0', 't306-1', 't842-0', 't454-0', 't0-0', 't0-1', 'q1', 'm1', 'm2', 'm3', 'l1', 'l2']
NAMED = (454, 157, 306, 70, 91, 264, 842, 545, 19, 87)


def arm_of(g, s):
    src = g['src']
    t = g['t'][s]
    if src == 'top3':
        return 'f%d' % t if t in NAMED else 'fopp'
    if src == 'top1':
        return 'o%d' % t if t in NAMED else 'oopp'
    lab = {'agg8-q1': 'B7Q', 'agg7-m1': 'MAIN', 'agg7-m2': 'MAIN', 'agg7-m3': 'MAIN', 'top-l1': 'L1', 'top-l2': 'L2'}[src]
    if s == 0:
        return lab
    if lab in ('L1', 'L2'):
        return 'v%d' % t
    return 'x' + lab


def dk(d):
    return 'a' if d <= 3 else 'b' if d <= 5 else 'c'


def pct(a, b):
    return '%.0f' % (100.0 * a / b) if b else '-'


def per(a, b, k=100.0):
    return '%.1f' % (k * a / b) if b else '-'


def main():
    want = sys.argv[1:]
    C = defaultdict(Counter)
    for tag in FILES:
        p = W / ('tq2_near-%s.jsonl' % tag)
        if not p.exists():
            continue
        with open(p) as fh:
            for line in fh:
                if not line.strip():
                    continue
                g = json.loads(line)
                for s in (0, 1):
                    c = C[arm_of(g, s)]
                    c['games'] += 1
                    c['turns'] += sum(g['turns'][s])
                    c['turns12'] += g['turns'][s][1] + g['turns'][s][2]
                    f = g['fate'][s]
                    ramturn = f[4] if f is not None and f[2] == 3 and not f[3] else -99
                    recs = g['recs'][s]
                    byidx = {r[17]: r for r in recs}
                    for r in recs:
                        d = r[2]
                        k = dk(d)
                        mid = 50 < r[0] <= 300
                        c['n' + k] += 1
                        c['n%d' % d] += 1
                        if mid:
                            c['m' + k] += 1
                        if r[7] > 0:
                            a = 'split'
                        elif r[12]:
                            a = 'died'
                        elif r[6] >= 2:
                            a = 'sprint'
                        elif r[3] > d:
                            a = 'away'
                        elif r[3] == d:
                            a = 'level'
                        else:
                            a = 'closer'
                        c[k + '_' + a] += 1
                        c['%d_%s' % (d, a)] += 1
                        Lk = 'L2' if r[1] <= 2 else 'L3' if r[1] == 3 else 'L4'
                        c[k + Lk] += 1
                        c[k + Lk + '_' + a] += 1
                        if r[6] >= 2:
                            c[k + '_paid'] += int(r[6] > (r[1] + 3) // 4)
                        # Manhattan response (what a radius term in the bot would see)
                        m = r[4]
                        if m <= 8 and r[6] >= 1 and not r[12]:
                            mk = 'M%d' % m
                            c[mk] += 1
                            c[mk + ('_away' if r[5] > m else '_level' if r[5] == m else '_closer')] += 1
                        c[k + '_ram5'] += int(0 <= ramturn - r[17] < 5)
                        c[k + '_ram1'] += r[13]
                        c['%d_ram5' % d] += int(0 <= ramturn - r[17] < 5)
                        c[k + '_ate'] += int(r[11] > 0)
                        c[k + '_mn'] += r[14]
                        c[k + '_o5'] += r[8]
                        if k == 'b':
                            nx = byidx.get(r[17] + 1)
                            if r[12] or (f is not None and f[4] == r[17]):
                                c['b_next_dead'] += 1
                            elif nx is None:
                                c['b_next_far'] += 1
                            else:
                                c['b_next_' + dk(nx[2])] += 1
    order = [a for a in ('f454', 'f70', 'f306', 'f157', 'f91', 'f545', 'f19', 'fopp', 'o306', 'o91', 'o264', 'o842', 'o545', 'o19', 'o87', 'oopp', 'v157', 'v306', 'v454', 'v87',
                         'xB7Q', 'xMAIN', 'B7Q', 'MAIN', 'L1', 'L2') if a in C and (not want or a in want)]
    print('== N1. turns per 100 of hers with the nearest enemy head (not the queen) at 1-3 / 4-5 / 6-8 steps; share of the within-5 turns that are within 3 (%); same share in r51-300')
    for a in order:
        c = C[a]
        t = c['turns']
        print(a, '|', c['games'], t, '|', per(c['na'], t), per(c['nb'], t), per(c['nc'], t), '|', pct(c['na'], c['na'] + c['nb']), '|', pct(c['ma'], c['ma'] + c['mb']))
    print('\n== N2. what she does, by distance band (1-3 | 4-5 | 6-8): away/level/closer/sprint/split/died on move (%)')
    for a in order:
        c = C[a]
        out = []
        for k in 'abc':
            n = c['n' + k]
            out.append('%d: ' % n + '/'.join(pct(c[k + '_' + x], n) for x in ('away', 'level', 'closer', 'sprint', 'split', 'died')))
        print(a, '|', ' | '.join(out))
    print('\n== N3. step away share (%) of single steps at each distance 1..8 (away / (away+level+closer)); n at 4, 5')
    for a in order:
        c = C[a]
        out = []
        for d in range(1, 9):
            n = c['%d_away' % d] + c['%d_level' % d] + c['%d_closer' % d]
            out.append(pct(c['%d_away' % d], n))
        print(a, '|', ' '.join(out), '|', c['n4'], c['n5'])
    print('\n== N3m. same by Manhattan tiles 1..8 (moved turns): away share; closer share')
    for a in order:
        c = C[a]
        print(a, '|', ' '.join(pct(c['M%d_away' % d], c['M%d' % d]) for d in range(1, 9)), '|', ' '.join(pct(c['M%d_closer' % d], c['M%d' % d]) for d in range(1, 9)))
    print('\n== N4. at 4-5 steps: by her length 2 / 3 / 4+: n: away/level/closer/sprint/split (%)')
    for a in order:
        c = C[a]
        out = []
        for Lk in ('L2', 'L3', 'L4'):
            n = c['b' + Lk]
            out.append('%d: ' % n + '/'.join(pct(c['b' + Lk + '_' + x], n) for x in ('away', 'level', 'closer', 'sprint', 'split')))
        print(a, '|', ' | '.join(out))
    print('\n== N5. from 4-5 steps, her next turn starts with the nearest at: 1-3 / 4-5 / 6-8 / none within 8 / she is dead (%); rammed within 5 of her turns from 1-3 | 4-5 | 6-8 (%); per distance 1..8')
    for a in order:
        c = C[a]
        n = c['nb']
        print(a, '|', '/'.join(pct(c['b_next_' + x], n) for x in ('a', 'b', 'c', 'far', 'dead')), '|', per(c['a_ram5'], c['na']), per(c['b_ram5'], c['nb']), per(c['c_ram5'], c['nc']), '|',
              ' '.join(per(c['%d_ram5' % d], c['n%d' % d]) for d in range(1, 9)))
    print('\n== N6. at 1-3 | 4-5 | 6-8: a mate nearer that head than she is (%); own heads within 5 tiles (mean); she eats that turn (%)')
    for a in order:
        c = C[a]
        print(a, '|', ' | '.join('%s %s %s' % (pct(c[k + '_mn'], c['n' + k]), per(c[k + '_o5'], c['n' + k], 1), pct(c[k + '_ate'], c['n' + k])) for k in 'abc'))


main()

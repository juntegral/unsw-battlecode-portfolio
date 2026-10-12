"""Scratch (diag-wipeout): what a pressed side does. From wo_scan rows: turns that begin with an enemy head within
2 tiles (contact turns) and how they end (rams it, ends farther, nearer, same distance, dies otherwise), plus spacing
samples and split rate. Four populations: (a) side 0 in its wipe-out games, the 60 rounds up to the half round;
(b) side 0 in its other games on the same layouts, the same rounds as (a) on that layout; (c) the opponents in (a).
Usage: python3 data/analysis/ladder/dossier/work/wo_press.py <O|L|R>"""
import sys, json
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')


def load(src):
    rows = []
    for p in sorted(WORK.glob('wo_scan-' + src + '[0-9].jsonl')):
        for line in p.read_text().splitlines():
            rows.append(json.loads(line))
    return rows


def marks(g):
    al = [x[0] for x in g['snap']]
    peak = max(al)
    pr = max(r for r, a in enumerate(al) if a == peak)
    hr = next((r for r in range(pr, len(al)) if al[r] * 2 < peak), None)
    return peak, pr, hr


def add(T, g, s, lo, hi):
    for r, sd, L0, Lt, d0, oc, n in g['contact']:
        if sd == s and lo < r <= hi:
            rel = 'longer' if Lt > L0 else 'shorter' if Lt < L0 else 'equal'
            for key in ('all', rel, 'own 2-4' if L0 <= 4 else 'own 5+'):
                T[(key, oc)] += n
                T[(key, 'n')] += n
    for x in g['rc']:
        if lo < x[0] <= hi:
            T[('turns', 'n')] += x[1 + s * 5]
            T[('splits', 'n')] += x[2 + s * 5]
            T[('eats', 'n')] += x[3 + s * 5] + x[4 + s * 5]
    for x in g['samples']:
        if lo < x[0] <= hi:
            v = x[1 + s * 6:7 + s * 6]
            T[('heads', 'n')] += v[0]
            T[('near own', 'n')] += v[1]
            T[('alone', 'n')] += v[2]
            T[('foe3', 'n')] += v[3]
            T[('foe dist', 'n')] += v[4]
            T[('len2', 'n')] += v[5]
    for d in g['deaths']:
        if d['s'] == s and lo < d['r'] <= hi:
            T[('deaths', 'n')] += 1
            if d['c'] == 'head-on' and d.get('cross'):
                T[('deaths', 'mover' if d['role'] == 'mover' else 'hit')] += 1


def show(name, T, games):
    t = max(T[('turns', 'n')], 1)
    h = max(T[('heads', 'n')], 1)
    print('%s: %d games, %d turns | splits %.2f, eats %.2f, deaths %.2f per 100 turns | cross head-ons: mover %d, hit %d (mover share %.0f%%)' % (
        name, games, t, 100 * T[('splits', 'n')] / t, 100 * T[('eats', 'n')] / t, 100 * T[('deaths', 'n')] / t,
        T[('deaths', 'mover')], T[('deaths', 'hit')], 100 * T[('deaths', 'mover')] / max(T[('deaths', 'mover')] + T[('deaths', 'hit')], 1)))
    print('   spacing (5-round samples): own heads within 5 per dragon %.2f, none within 5 %.0f%%, an enemy head within 3 %.0f%%, mean gap to nearest enemy head %.1f, length 2 %.0f%%' % (
        T[('near own', 'n')] / h, 100 * T[('alone', 'n')] / h, 100 * T[('foe3', 'n')] / h, T[('foe dist', 'n')] / h, 100 * T[('len2', 'n')] / h))
    for key in ('all', 'longer', 'equal', 'shorter', 'own 2-4', 'own 5+'):
        n = T[(key, 'n')]
        if n:
            print('   contact turns, %-8s %6d (%.1f%% of turns): rams %.1f%%, farther %.0f%%, nearer %.0f%%, same %.0f%%, dies otherwise %.1f%%' % (
                key if key in ('all', 'own 2-4', 'own 5+') else 'target ' + key, n, 100 * n / t, 100 * T[(key, 'R')] / n, 100 * T[(key, 'A')] / n, 100 * T[(key, 'C')] / n,
                100 * T[(key, 'S')] / n, 100 * T[(key, 'D')] / n))


def main():
    src = sys.argv[1]
    rows = load(src)
    out = [g for g in rows if g['final'][0] == 0]
    rest = [g for g in rows if g['final'][0] != 0]
    A, B, C = Counter(), Counter(), Counter()
    windows = defaultdict(list)
    for g in out:
        peak, pr, hr = marks(g)
        lo = max(0, hr - 60)
        add(A, g, 0, lo, hr)
        add(C, g, 1, lo, hr)
        windows[g['layout']].append((lo, hr))
    nb = 0
    for g in rest:
        ws = windows.get(g['layout'])
        if not ws:
            continue
        nb += 1
        tmp = Counter()
        for lo, hr in ws:
            add(tmp, g, 0, lo, hr)
        for k, v in tmp.items():
            B[k] += v / len(ws)
    show(src + ' (a) side 0 in its wipe-outs, 60 rounds to the half round', A, len(out))
    show(src + ' (c) the opponents in those rounds', C, len(out))
    show(src + ' (b) side 0 in its other games on the same layouts, same rounds', B, nb)


main()

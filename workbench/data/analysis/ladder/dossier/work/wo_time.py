"""Scratch (diag-wipeout): timing of the first pearls and splits on two-dragon starts (total length 6 or less,
1200 cells or fewer), by outcome class; from wo_scan rows (rc = per round turns, splits, natural eats, drop eats).
Usage: python3 data/analysis/ladder/dossier/work/wo_time.py <O|L|R> [nostripes]"""
import sys, json
sys.dont_write_bytecode = True
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')


def load(src):
    rows = []
    for p in sorted(WORK.glob('wo_scan-' + src + '[0-9].jsonl')):
        for line in p.read_text().splitlines():
            g = json.loads(line)
            g.pop('contact', None)
            g.pop('samples', None)
            rows.append(g)
    return rows


def cls(g):
    return 'OUT' if g['final'][0] == 0 else 'KILL' if g['final'][4] == 0 else 'REST'


def med(v):
    v = sorted(999 if x is None else x for x in v)
    return v[len(v) // 2] if v else None


def kth(g, s, k, what):
    n = 0
    for x in g['rc']:
        v = x[1:]
        n += (v[s * 5 + 2] + v[s * 5 + 3]) if what == 'eat' else v[s * 5 + 1]
        if n >= k:
            return x[0]
    return None


def main():
    src = sys.argv[1]
    rows = [g for g in load(src) if g['cells'] <= 1200 and g['snap'][0][0] == 2 and g['snap'][0][1] <= 6]
    if len(sys.argv) > 2:
        rows = [g for g in rows if g['map'] != 'Stripes']
    print(src, 'two-dragon starts', len(rows), dict(Counter(cls(g) for g in rows)), dict(Counter(g['map'] for g in rows)))
    for c in ('OUT', 'KILL', 'REST'):
        a = [g for g in rows if cls(g) == c]
        if not a:
            continue
        print(c, len(a), 'by map', dict(Counter(g['map'] for g in a)))
        for what in ('eat', 'split'):
            print('   median round of %s number k, us/them: ' % what + ' '.join('k%d %s/%s' % (k, med([kth(g, 0, k, what) for g in a]), med([kth(g, 1, k, what) for g in a])) for k in (1, 2, 3, 4, 6, 8)))
        first = Counter()
        for g in a:
            u, t = kth(g, 0, 1, 'split'), kth(g, 1, 1, 'split')
            u = 999 if u is None else u
            t = 999 if t is None else t
            first['we split first' if u < t else 'they split first' if t < u else 'same round'] += 1
        print('   first split:', dict(first))
        # count just before the first cross-team head-on, and who has more then
        pre = Counter()
        rr = []
        for g in a:
            ho = [d for d in g['deaths'] if d['c'] == 'head-on' and d.get('cross')]
            if not ho:
                pre['no head-on'] += 1
                continue
            r = ho[0]['r']
            rr.append(r)
            sn = g['snap'][max(r - 1, 0)]
            pre['we have more' if sn[0] > sn[4] else 'they have more' if sn[4] > sn[0] else 'level'] += 1
        print('   at the first cross head-on (median r%s): %s' % (med(rr), dict(pre)))
    # outcome by who splits first
    tab = defaultdict(Counter)
    for g in rows:
        u, t = kth(g, 0, 2, 'split'), kth(g, 1, 2, 'split')
        u = 999 if u is None else u
        t = 999 if t is None else t
        tab['we reach 2 splits first' if u < t else 'they do' if t < u else 'same'][cls(g)] += 1
    print('outcome by who makes its second split first:', dict((k, dict(v)) for k, v in tab.items()))
    tab = defaultdict(Counter)
    for g in rows:
        r = 30
        sn = g['snap'][min(r, g['last'])]
        tab['we have more at r30' if sn[0] > sn[4] else 'they have more' if sn[4] > sn[0] else 'level'][cls(g)] += 1
    print('outcome by count at r30:', dict((k, dict(v)) for k, v in tab.items()))


main()

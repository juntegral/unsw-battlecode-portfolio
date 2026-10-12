"""Scratch (diag-wipeout): per layout, how games end (OUT = we have no dragon left, KILL = they have none, REST),
for the online set (O), our ladder games (L) and rank-1's (R); peak-count distribution of the OUT games; the round
the other side first holds twice our count for good. Usage: python3 data/analysis/ladder/dossier/work/wo_lay.py"""
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


def size(c):
    return '<=700' if c <= 700 else '701-1200' if c <= 1200 else '>1200'


def cls(g):
    return 'OUT' if g['final'][0] == 0 else 'KILL' if g['final'][4] == 0 else 'REST'


def med(v):
    v = sorted(v)
    return v[len(v) // 2] if v else None


def diverge(g, s=0):
    """first round from which the other side holds at least twice side s's count until the end"""
    sn = g['snap']
    r = len(sn)
    while r > 0 and sn[r - 1][4 * (1 - s)] >= 2 * sn[r - 1][4 * s]:
        r -= 1
    return r


def main():
    data = dict((src, load(src)) for src in 'OLR')
    names = {}
    for src in 'OLR':
        for g in data[src]:
            names.setdefault(g['layout'], (g['map'], g['W'], g['H'], g['snap'][0][0], g['snap'][0][1]))
    print('layout (map WxH, start dragons/length) | online OUT/KILL/REST(win) | our ladder OUT/KILL/REST(win) | rank-1 OUT/KILL/REST(win)')
    for lay, (nm, W, H, n0, t0) in sorted(names.items(), key=lambda t: t[1][1] * t[1][2]):
        cells = []
        for src in 'OLR':
            a = [g for g in data[src] if g['layout'] == lay]
            c = Counter(cls(g) for g in a)
            cells.append('%d: %d/%d/%d(%d)' % (len(a), c['OUT'], c['KILL'], c['REST'], sum(g['result'] == 'win' and cls(g) == 'REST' for g in a)))
        print('%-18s %dx%d=%d start %d/%d | %s' % (nm[:18], W, H, W * H, n0, t0, ' | '.join(cells)))
    for src in 'OLR':
        rows = data[src]
        out = [g for g in rows if cls(g) == 'OUT']
        print(src, 'games', len(rows), 'OUT', len(out), 'KILL', sum(cls(g) == 'KILL' for g in rows))
        for sz in ('<=700', '701-1200', '>1200'):
            a = [g for g in rows if size(g['cells']) == sz]
            o = [g for g in a if cls(g) == 'OUT']
            print('   %s games %d OUT %d (%.1f%%) KILL %d (%.1f%%) | share of all OUT %.0f%%' % (sz, len(a), len(o), 100 * len(o) / max(len(a), 1),
                  sum(cls(g) == 'KILL' for g in a), 100 * sum(cls(g) == 'KILL' for g in a) / max(len(a), 1), 100 * len(o) / max(len(out), 1)))
        if not out:
            continue
        pk = [max(x[0] for x in g['snap']) for g in out]
        print('   OUT peak count: <=5 %d, 6-10 %d, 11-20 %d, 21-40 %d, 41+ %d | median %d' % (
            sum(p <= 5 for p in pk), sum(6 <= p <= 10 for p in pk), sum(11 <= p <= 20 for p in pk), sum(21 <= p <= 40 for p in pk), sum(p > 40 for p in pk), med(pk)))
        dv = [diverge(g) for g in out]
        print('   OUT: round from which they hold twice our count for good: median r%d, by r50 %d, r51-100 %d, r101-200 %d, later %d' % (
            med(dv), sum(d <= 50 for d in dv), sum(50 < d <= 100 for d in dv), sum(100 < d <= 200 for d in dv), sum(d > 200 for d in dv)))
        print('   OUT: last death median r%d; our count at r50 median %d, theirs %d; at r100 %d / %d' % (
            med([g['last'] for g in out]), med([g['snap'][min(50, g['last'])][0] for g in out]), med([g['snap'][min(50, g['last'])][4] for g in out]),
            med([g['snap'][min(100, g['last'])][0] for g in out]), med([g['snap'][min(100, g['last'])][4] for g in out])))
        # deaths of ours before the divergence round, by kind
        kinds = Counter()
        n_before = 0
        for g, d in zip(out, dv):
            for x in g['deaths']:
                if x['s'] == 0 and x['r'] <= d:
                    n_before += 1
                    c = x['c']
                    if c == 'head-on':
                        c = 'mate head-on' if not x['cross'] else 'rammed' if x['role'] == 'hit' else 'rams'
                    elif c == 'other body':
                        c = 'body-' + x.get('hit', '?')
                    kinds[c] += 1
        print('   OUT: our deaths up to that round: %.1f a game: %s' % (n_before / len(out), ', '.join('%s %d' % kv for kv in kinds.most_common())))
        # same for KILL games: their divergence (we hold twice theirs)
        kill = [g for g in rows if cls(g) == 'KILL']
        if kill:
            dk = [diverge(g, 1) for g in kill]
            print('   KILL: round from which we hold twice their count for good: median r%d' % med(dk))


main()

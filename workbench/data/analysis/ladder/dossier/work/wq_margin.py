"""Scratch (diag-whq): what decides each game and how the gap in the deciding quantity came about.
Usage: python3 .../wq_margin.py [O|R|L] [list]"""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
ARM = {'agg7-m1': 'MAIN', 'agg7-m2': 'MAIN', 'agg7-m3': 'MAIN', 'agg7-b1': 'B7', 'agg7-b2': 'B7', 'agg8-q1': 'B7Q', 'agg8-q2': 'B7Q'}


def load(prefix):
    rows = []
    for p in sorted(WORK.glob(prefix)):
        for line in p.read_text().splitlines():
            rows.append(json.loads(line))
    return rows


def med(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else None


def decided(g):
    f = g['final']
    if f[0] == 0 or f[4] == 0:
        return 'E'
    if f[3] != f[7]:
        return 'Q'
    if f[2] != f[6]:
        return 'L'
    return 'T'


def qdeath(g, s):
    for d in g['deaths']:
        if d['s'] == s and d['q']:
            return d
    return None


def describe(d):
    if d is None:
        return 'alive'
    c = d['c']
    if c == 'head-on':
        if d['role'] == 'hit':
            m = d['m']
            return 'r%d rammed L%d by L%d k%d paid%d' % (d['r'], d['L'], m['L0'], m['steps'], m['paid'])
        return 'r%d rams L%d' % (d['r'], d['L'])
    return 'r%d %s L%d' % (d['r'], c, d['L'])


def passed(g, k):
    """first round from which side 1 is ahead in snapshot field k for good"""
    sn = g['snap']
    last = -1
    for r, st in enumerate(sn):
        if st is not None and st[4 + k] <= st[k]:
            last = r
    return last + 1


def summary(rows, title):
    n = len(rows)
    if not n:
        return
    loss = [g for g in rows if g['result'] == 'loss']
    win = [g for g in rows if g['result'] == 'win']
    print()
    print('==', title, 'games', n, 'won', len(win), 'lost', len(loss))
    for res, rs in (('loss', loss), ('win', win)):
        c = Counter(decided(g) for g in rs)
        print(' ', res, 'decided by E/Q/L/T:', c['E'], c['Q'], c['L'], c['T'])
    # losses by class
    for k in ('E', 'Q', 'L'):
        rs = [g for g in loss if decided(g) == k]
        if not rs:
            continue
        print('  -- losses decided by', k, len(rs), '| cells <=700; 701-1200; >1200:', sum(1 for g in rs if g['cells'] <= 700), sum(1 for g in rs if 700 < g['cells'] <= 1200), sum(1 for g in rs if g['cells'] > 1200))
        f = [g['final'] for g in rs]
        print('     final ours: alive %.1f total %.0f longest %.1f queen %.1f | theirs: alive %.1f total %.0f longest %.1f queen %.1f' % tuple(sum(x[i] for x in f) / len(f) for i in range(8)))
        oq = [qdeath(g, 0) for g in rs]
        tq = [qdeath(g, 1) for g in rs]
        print('     our queen: alive %d, rammed %d, own move %d; death round median %s | their queen: alive %d, rammed %d, own move %d' % (
            sum(1 for d in oq if d is None), sum(1 for d in oq if d is not None and d['c'] == 'head-on' and d['role'] == 'hit'),
            sum(1 for d in oq if d is not None and not (d['c'] == 'head-on' and d['role'] == 'hit')), med([d['r'] for d in oq if d is not None]),
            sum(1 for d in tq if d is None), sum(1 for d in tq if d is not None and d['c'] == 'head-on' and d['role'] == 'hit'),
            sum(1 for d in tq if d is not None and not (d['c'] == 'head-on' and d['role'] == 'hit'))))
        if k == 'Q':
            print('     their queen ahead for good from round (median) %s; her length at the end median %s; ours %s' % (med([passed(g, 3) for g in rs]), med([g['final'][7] for g in rs]), med([g['final'][3] for g in rs])))
        if k == 'L':
            print('     their longest ahead for good from round (median) %s; lengths at the end median %s against %s' % (med([passed(g, 2) for g in rs]), med([g['final'][6] for g in rs]), med([g['final'][2] for g in rs])))
        if k == 'E':
            print('     last round median %s; their count ahead for good from (median) %s' % (med([g['last'] for g in rs]), med([passed(g, 0) for g in rs])))
        # timeline of both sides in these games
        for cp in (50, 100, 150, 200, 300, 400):
            st = [g['snap'][min(cp, g['last'])] for g in rs]
            print('     r%d ours alive %.1f total %.0f longest %.1f queen %.2f (alive in %d) | theirs %.1f %.0f %.1f %.2f (%d)' % (
                cp, sum(x[0] for x in st) / len(st), sum(x[1] for x in st) / len(st), sum(x[2] for x in st) / len(st), sum(x[3] for x in st) / len(st), sum(1 for x in st if x[3]),
                sum(x[4] for x in st) / len(st), sum(x[5] for x in st) / len(st), sum(x[6] for x in st) / len(st), sum(x[7] for x in st) / len(st), sum(1 for x in st if x[7])))
    # ledger over all games of the group: length gained and lost per side
    for res, rs in (('losses', loss), ('wins', win)):
        if not rs:
            continue
        led = [Counter(), Counter()]
        for g in rs:
            for w, sd, c, o, q, v in g['E']:
                led[sd][('eat', o)] += v
            for w, sd, c, kk, v in g['MV']:
                if kk == 'paid segs':
                    led[sd]['paid'] += v
            for d in g['deaths']:
                c = d['c']
                if c == 'head-on':
                    c = ('rams' if d['role'] == 'mover' else 'rammed') if d['cross'] else 'mate head'
                elif c == 'other body':
                    c = 'body ' + d.get('hit', '?')
                elif c not in ('wall', 'own body'):
                    c = 'no order'
                led[d['s']][('die', c)] += d['L']
                led[d['s']][('n', c)] += 1
        for sd, nm in ((0, 'ours'), (1, 'theirs')):
            L = led[sd]
            m = len(rs)
            print('  ledger %s, %s, a game: eats natural %.1f own dead %.1f their dead %.1f | paid in sprints %.1f | dies: ' % (res, nm, L[('eat', 0)] / m, L[('eat', 1)] / m, L[('eat', 2)] / m, L['paid'] / m) +
                  '; '.join('%s %.1f (%.1f dragons)' % (k[1], v / m, L[('n', k[1])] / m) for k, v in sorted(L.items(), key=lambda t: -t[1]) if isinstance(k, tuple) and k[0] == 'die'))


def listing(rows):
    for g in sorted(rows, key=lambda g: (g['opp'], ARM.get(g['src'], g['src']), g['gid'])):
        f = g['final']
        k = decided(g)
        print('%s %-4s %d %-16s %dx%d %s by %s r%d | ours a%d t%d l%d q%d | theirs a%d t%d l%d q%d | our Q %s | their Q %s | ahead from r%s' % (
            g['opp'][:4], ARM.get(g['src'], g['src']), g['gid'], g['map'], g['W'], g['H'], g['result'], k, g['last'], f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7],
            describe(qdeath(g, 0)), describe(qdeath(g, 1)), passed(g, {'E': 0, 'Q': 3, 'L': 2, 'T': 1}[k]) if g['result'] == 'loss' else '-'))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'O'
    if mode == 'R':
        rows = load('wq_scan-R[0-9].jsonl')
        summary(rows, 'rank-1 (side 0 = rank-1)')
        return
    if mode == 'L':
        rows = load('wq_scan-L[0-9].jsonl')
        summary(rows, 'our ladder')
        return
    rows = load('wq_scan-O[0-9].jsonl')
    if len(sys.argv) > 2:
        listing(rows)
        return
    for opp in ('WeHaveQuizzes', 'Big Bobs Bots'):
        for arm in ('MAIN', 'B7', 'B7Q'):
            summary([g for g in rows if ARM[g['src']] == arm and g['opp'] == opp], opp + ' ' + arm)
        summary([g for g in rows if g['opp'] == opp], opp + ' all arms')


main()

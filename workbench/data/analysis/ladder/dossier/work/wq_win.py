"""Scratch (diag-whq): the length account of both sides by round window, a game.
Usage: python3 .../wq_win.py <O|R|L> [opponent prefix] [arm] [loss|win] [size: S|M|B]"""
import sys, json
from collections import Counter
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')
ARM = {'agg7-m1': 'MAIN', 'agg7-m2': 'MAIN', 'agg7-m3': 'MAIN', 'agg7-b1': 'B7', 'agg7-b2': 'B7', 'agg8-q1': 'B7Q', 'agg8-q2': 'B7Q'}
WN = ('0-40', '41-100', '101-200', '201-300', '301-400', '401+')
KINDS = ('rammed', 'rams', 'boxed', 'own move', 'mate', 'enemy body', 'no order')


def wnd(r):
    return 0 if r <= 40 else 1 if r <= 100 else 2 if r <= 200 else 3 if r <= 300 else 4 if r <= 400 else 5


def load(prefix):
    rows = []
    for p in sorted(WORK.glob(prefix)):
        for line in p.read_text().splitlines():
            rows.append(json.loads(line))
    return rows


def kind(d):
    c = d['c']
    if c == 'head-on':
        if not d['cross']:
            return 'mate'
        return 'rams' if d['role'] == 'mover' else 'rammed'
    if c == 'other body':
        return 'mate' if d.get('hit') == 'mate' else 'enemy body'
    if d.get('free', 1) == 0:
        return 'boxed'
    if c in ('wall', 'own body'):
        return 'own move'
    return 'no order'


def account(rows, title):
    n = len(rows)
    if not n:
        print(title, 'no games')
        return
    print()
    print('==', title, '| games', n, '| won by side 0:', sum(1 for g in rows if g['result'] == 'win'))
    A = Counter()
    played = Counter()
    for g in rows:
        for w in range(6):
            if g['last'] >= (0, 41, 101, 201, 301, 401)[w]:
                played[w] += 1
        for w, sd, c, z, q, v in g['T']:
            A[(w, sd, 'turns')] += v
            if c <= 1:
                A[(w, sd, 'short turns')] += v
        for w, sd, c, o, q, v in g['E']:
            A[(w, sd, 'eat%d' % o)] += v
            if q:
                A[(w, sd, 'qeat')] += v
            if c >= 3:
                A[(w, sd, 'longeat')] += v
        for w, sd, lb, lc, q, v in g['S']:
            A[(w, sd, 'splits')] += v
        for w, sd, c, kk, v in g['MV']:
            if kk == 'paid segs':
                A[(w, sd, 'paid')] += v
        for d in g['deaths']:
            w = wnd(d['r'])
            k = kind(d)
            A[(w, d['s'], 'n ' + k)] += 1
            A[(w, d['s'], 'L ' + k)] += d['L']
            A[(w, d['s'], 'deaths')] += 1
            A[(w, d['s'], 'lost')] += d['L']
            for sd in (0, 1):
                A[(w, sd, 'eat of %d' % d['s'])] += 0
    print('window | games | side | turns | pearls: natural, own dead, their dead | splits | deaths (length) | of them: ' + ', '.join(KINDS) + ' | paid | net length | pearls /1k turns')
    for w in range(6):
        for sd, nm in ((0, 'side0'), (1, 'side1')):
            eat = sum(A[(w, sd, 'eat%d' % o)] for o in range(3))
            net = eat - A[(w, sd, 'lost')] - A[(w, sd, 'paid')]
            print('%s | %d | %s | %.0f | %.1f, %.1f, %.1f | %.1f | %.1f (%.1f) | %s | %.1f | %+.1f | %.1f' % (
                WN[w], played[w], nm, A[(w, sd, 'turns')] / n, A[(w, sd, 'eat0')] / n, A[(w, sd, 'eat1')] / n, A[(w, sd, 'eat2')] / n,
                A[(w, sd, 'splits')] / n, A[(w, sd, 'deaths')] / n, A[(w, sd, 'lost')] / n,
                ', '.join('%.1f' % (A[(w, sd, 'n ' + k)] / n) for k in KINDS), A[(w, sd, 'paid')] / n, net / n,
                1000 * eat / max(1, A[(w, sd, 'turns')])))
    for sd, nm in ((0, 'side0'), (1, 'side1')):
        tot = Counter()
        for (w, s2, k), v in A.items():
            if s2 == sd:
                tot[k] += v
        eat = sum(tot['eat%d' % o] for o in range(3))
        print('game %s: pearls %.1f (natural %.1f, own dead %.1f, their dead %.1f); lost in deaths %.1f: %s; paid %.1f; net %+.1f' % (
            nm, eat / n, tot['eat0'] / n, tot['eat1'] / n, tot['eat2'] / n, tot['lost'] / n,
            ', '.join('%s %.1f dragons %.1f length' % (k, tot['n ' + k] / n, tot['L ' + k] / n) for k in KINDS), tot['paid'] / n,
            (eat - tot['lost'] - tot['paid']) / n))


def main():
    mode = sys.argv[1]
    if mode == 'O':
        rows = load('wq_scan-O[0-9].jsonl')
        opp = sys.argv[2] if len(sys.argv) > 2 else ''
        arm = sys.argv[3] if len(sys.argv) > 3 else 'all'
        res = sys.argv[4] if len(sys.argv) > 4 else 'all'
        size = sys.argv[5] if len(sys.argv) > 5 else 'all'
        rows = [g for g in rows if g['opp'].startswith(opp) and (arm == 'all' or ARM[g['src']] == arm) and (res == 'all' or g['result'] == res)
                and (size == 'all' or (size == 'S' and g['cells'] <= 700) or (size == 'M' and 700 < g['cells'] <= 1200) or (size == 'B' and g['cells'] > 1200))]
        account(rows, 'online %s %s %s %s (side0 = ours)' % (opp, arm, res, size))
    else:
        rows = load('wq_scan-%s[0-9].jsonl' % mode)
        res = sys.argv[2] if len(sys.argv) > 2 else 'all'
        rows = [g for g in rows if res == 'all' or g['result'] == res]
        account(rows, mode + ' ' + res)


main()

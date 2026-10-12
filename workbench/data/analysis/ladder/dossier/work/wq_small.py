"""Scratch (diag-whq): boards of 1200 cells or fewer, rounds 0-60: who dies of what, by opponent and by how the game ends.
Usage: python3 .../wq_small.py [O|R]"""
import sys, json
from collections import Counter
from pathlib import Path

WORK = Path('data/analysis/ladder/dossier/work')


def load(prefix):
    rows = []
    for p in sorted(WORK.glob(prefix)):
        for line in p.read_text().splitlines():
            rows.append(json.loads(line))
    return rows


def decided(g):
    f = g['final']
    if f[0] == 0 or f[4] == 0:
        return 'E'
    if f[3] != f[7]:
        return 'Q'
    if f[2] != f[6]:
        return 'L'
    return 'T'


def kind(d):
    c = d['c']
    if c == 'head-on':
        if not d['cross']:
            return 'mate'
        if d['role'] == 'mover':
            return 'rams'
        return 'rammed1' if d['m']['steps'] == 1 else 'rammed2+'
    if c == 'other body':
        return 'mate' if d.get('hit') == 'mate' else 'enemy body'
    if d.get('free', 1) == 0:
        return 'boxed'
    return 'own move'


KINDS = ('rammed1', 'rammed2+', 'rams', 'boxed', 'own move', 'mate', 'enemy body')


def block(rows, title):
    n = len(rows)
    if not n:
        return
    print()
    print('==', title, 'games', n)
    for lo, hi in ((0, 20), (21, 40), (41, 60), (61, 100)):
        c = [Counter(), Counter()]
        for g in rows:
            for d in g['deaths']:
                if lo <= d['r'] <= hi:
                    c[d['s']][kind(d)] += 1
        eat = [0, 0]
        for g in rows:
            for row in g['rc']:
                if lo <= row[0] <= hi:
                    eat[0] += row[3] + row[4]
                    eat[1] += row[8] + row[9]
        print('  r%d-%d ours: pearls %.1f deaths %s | theirs: pearls %.1f deaths %s' % (
            lo, hi, eat[0] / n, ' '.join('%s %.2f' % (k, c[0][k] / n) for k in KINDS), eat[1] / n, ' '.join('%s %.2f' % (k, c[1][k] / n) for k in KINDS)))
    for cp in (20, 30, 40, 60, 100):
        st = [g['snap'][min(cp, g['last'])] for g in rows]
        print('  r%d alive ours %.1f theirs %.1f | total %.1f %.1f' % (cp, sum(x[0] for x in st) / n, sum(x[4] for x in st) / n, sum(x[1] for x in st) / n, sum(x[5] for x in st) / n))
    # the first death of a starter of ours: queen or the other starter, by r60
    fd = Counter()
    for g in rows:
        ns = len(g['start_len'][0])
        for sd, nm in ((0, 'ours'), (1, 'theirs')):
            ds = [d for d in g['deaths'] if d['s'] == sd and d['r'] <= 40]
            rm = [d for d in ds if kind(d) in ('rammed1', 'rammed2+')]
            fd[(nm, 'games with a dragon rammed by r40')] += 1 if rm else 0
            fd[(nm, 'games with a dragon lost by r40 any cause')] += 1 if ds else 0
            st = g['snap'][min(40, g['last'])]
    print('  ', dict(fd))


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'O'
    rows = load('wq_scan-%s[0-9].jsonl' % mode)
    rows = [g for g in rows if g['cells'] <= 1200 and len(g['start_len'][0]) <= 2]
    print('two-dragon starts on 1200 cells or fewer:', len(rows), Counter(g['map'] for g in rows))
    if mode == 'O':
        for opp in ('WeHaveQuizzes', 'Big Bobs Bots'):
            rs = [g for g in rows if g['opp'] == opp]
            block(rs, opp + ' all')
            block([g for g in rs if g['result'] == 'loss' and decided(g) == 'E'], opp + ' we are eliminated')
            block([g for g in rs if g['result'] == 'win' and decided(g) == 'E'], opp + ' they are eliminated')
            block([g for g in rs if decided(g) != 'E'], opp + ' no elimination')
    else:
        block(rows, mode + ' all')
        block([g for g in rows if g['result'] == 'loss' and decided(g) == 'E'], mode + ' side 0 eliminated')
        block([g for g in rows if g['result'] == 'win' and decided(g) == 'E'], mode + ' side 1 eliminated')


main()

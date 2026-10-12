"""Scratch (diag-aahsplit): the report tables as markdown, every set side by side.
Usage: python3 as_md.py"""
import sys
import json
from collections import Counter, defaultdict
from pathlib import Path

WORKREL = 'data/analysis/ladder/dossier/work/'
TAGS = (('a', 'aAah fresh'), ('a0', 'aAah to 5 Oct'), ('l', 'larp fresh'), ('c1', 'Cutlery fresh'), ('g', 'chad gdp fresh'),
        ('q', 'ours B7Q'), ('m', 'ours main'), ('t', 'ours live v larp, Cutlery'))
CN = ('under 32', '32-43', '44-47', '48-51', '52-55', '56-59', '60-63')


def cc(a):
    return 0 if a < 32 else 1 if a < 44 else 2 if a < 48 else 3 if a < 52 else 4 if a < 56 else 5 if a < 60 else 6


def grp(L):
    return 0 if L <= 3 else 1 if L == 4 else 2 if L <= 8 else 3


def f1(a, b, k=100.0):
    return '%.1f' % (k * a / b) if b else '-'


def f0(a, b, k=100.0):
    return '%.0f' % (k * a / b) if b else '-'


def main():
    data = {}
    for tag, name in TAGS:
        p = Path(WORKREL + 'as_scan-' + tag + '.jsonl')
        data[tag] = [json.loads(x) for x in p.read_text().splitlines() if x]
    rows = defaultdict(list)

    def add(key, val):
        rows[key].append(val)
    order = []

    def row(key):
        if key not in order:
            order.append(key)
    for tag, name in TAGS:
        games = data[tag]
        n = len(games)
        S = [s for g in games for s in g['splits']]
        c = Counter()
        for g in games:
            for r in g['rows']:
                sp = int(r[16] >= 2)
                if r[3] >= 64:
                    k = 'cap'
                elif r[6] == 0:
                    k = 'boxed'
                elif r[4]:
                    k = 'queen'
                elif r[10] == 1:
                    k = 'pearl'
                    if r[2] == 4 and r[3] < 60:
                        c['pearl4', 't'] += 1
                        c['pearl4', 's'] += sp
                        c['pearl4', 'e'] += int(r[18] > 0)
                else:
                    k = cc(r[3])
                    L = 'L4' if r[2] == 4 else 'L5'
                    c[L, k, 't'] += 1
                    c[L, k, 's'] += sp
                    z = 0 if r[3] < 44 else 1 if r[3] < 56 else 2
                    c[L, 'z', z, 't'] += 1
                    c[L, 'z', z, 's'] += sp
                c[k, 't'] += 1
                c[k, 's'] += sp
        for key, val in (
                ('Games (won)', '%d (%d)' % (n, sum(1 for g in games if g['won'] == 1))),
                ('Splits a game; by a parent of exactly 4 %; with no free tile beside the head %', '%.0f; %s; %s' % (len(S) / n, f0(sum(1 for s in S if s[2] == 4), len(S)), f0(sum(1 for s in S if s[8] == 0), len(S)))),
                ('Splits of 5+: the parent keeps 2 %; a child of 2 leaves %', '%s; %s' % (f0(sum(1 for s in S if s[2] > 4 and s[4] == 2), sum(1 for s in S if s[2] > 4)), f0(sum(1 for s in S if s[2] > 4 and s[3] == 2 and s[4] > 2), sum(1 for s in S if s[2] > 4)))),
                ('1. No free tile beside the head: turns a game; split %', '%.0f; %s' % (c['boxed', 't'] / n, f1(c['boxed', 's'], c['boxed', 't']))),
                ('2. Pearl beside the head, a 4-long, under 60: turns a game; split %; eat %', '%.0f; %s; %s' % (c['pearl4', 't'] / n, f0(c['pearl4', 's'], c['pearl4', 't']), f0(c['pearl4', 'e'], c['pearl4', 't'])))):
            row(key)
            add(key, val)
        for k in range(7):
            key = '3. A 4-long, head free, no pearl beside, %s own dragons: split %%' % CN[k]
            row(key)
            add(key, f1(c['L4', k, 's'], c['L4', k, 't']) + ('*' if c['L4', k, 't'] < 200 else ''))
        key = '3. The same for 5 and longer: under 44; 44-55; 56-63'
        row(key)
        add(key, '; '.join(f1(c['L5', 'z', z, 's'], c['L5', 'z', z, 't']) for z in range(3)))
        key = 'Queen at 4+, head free: turns a game; split %'
        row(key)
        add(key, '%.0f; %s' % (c['queen', 't'] / n, f1(c['queen', 's'], c['queen', 't'])))
    print('### T1')
    print('| Rule row | ' + ' | '.join('%s' % name for tag, name in TAGS) + ' |')
    print('|---' * (len(TAGS) + 1) + '|')
    for key in order:
        print('| ' + key + ' | ' + ' | '.join(rows[key]) + ' |')

    # T5 by length r61-300
    rows = defaultdict(list)
    order[:] = []
    for tag, name in TAGS:
        games = data[tag]
        n = len(games)
        T = Counter()
        S2 = Counter()
        for g in games:
            for key, v in g['T'].items():
                W, L, nm = key.split('|')
                if int(W) in (2, 3):
                    T[grp(int(L)), nm] += v
                    T['L', int(L), nm] += v
            for key, v in g['SP'].items():
                W, G, paid, nm = key.split('|')
                if int(W) in (2, 3) and G == '2' and paid == '0':
                    S2[nm] += v
        tot = sum(T[z, 't'] for z in range(4))
        two = lambda z: T[z, 'n2'] + T[z, 'n3'] + T[z, 'n4']
        nn = S2['n']
        for key, val in (
                ('Share of turns % (2-3; 4; 5-8; 9+)', '; '.join(f1(T[z, 't'], tot) for z in range(4))),
                ('Turns of 2+ steps % (5-8; 9+)', '; '.join(f0(two(z), T[z, 't']) for z in (2, 3))),
                ('Pearls /1k turns (2-3; 4; 5-8; 9+)', '; '.join(f0(T[z, 'e'], T[z, 't'], 1000.0) for z in range(4))),
                ('Deaths /1k turns (2-3; 4; 5-8; 9+)', '; '.join(f1(T[z, 'd'], T[z, 't'], 1000.0) for z in range(4))),
                ('of them boxed in (2-3; 4; 5-8; 9+)', '; '.join(f1(T[z, 'dab'], T[z, 't'], 1000.0) for z in range(4))),
                ('Length lost /1k turns (2-3; 4; 5-8; 9+)', '; '.join(f0(T[z, 'll'], T[z, 't'], 1000.0) for z in range(4))),
                ('Rammed /1k turns at length 2; 3; 4; 5; 6; 7-8; 9+', '; '.join([f1(T['L', L, 'dv'], T['L', L, 't'], 1000.0) for L in (2, 3, 4, 5, 6)] +
                    [f1(T['L', 7, 'dv'] + T['L', 8, 'dv'], T['L', 7, 't'] + T['L', 8, 't'], 1000.0), f1(T[3, 'dv'], T[3, 't'], 1000.0)])),
                ('Rams started /1k turns (2-3; 4; 5-8; 9+)', '; '.join(f1(T[z, 'da3e'], T[z, 't'], 1000.0) for z in range(4))),
                ('Free two-step turns of a 5-8 a game', '%.0f' % (nn / n)),
                ('of them: two pearls; ends on its one pearl; eats on step 1 and goes on %', '; '.join(f1(S2[k], nn) for k in ('eat2', 'endp', 'eatgo'))),
                ('away from an enemy head within 3; nearer to one within 5; ram %', '; '.join(f1(S2[k], nn) for k in ('esc', 'app', 'ram'))),
                ('nearer to a pearl in reach; a pearl comes into reach; nothing of these %', '; '.join(f1(S2[k], nn) for k in ('topearl', 'found', 'plain'))),
                ('both steps the same way %', f0(S2['straight'], nn))):
            row(key)
            add(key, val)
    print('### T5')
    print('| Rounds 61-300 | ' + ' | '.join('%s' % name for tag, name in TAGS) + ' |')
    print('|---' * (len(TAGS) + 1) + '|')
    for key in order:
        print('| ' + key + ' | ' + ' | '.join(rows[key]) + ' |')

    # T7 timeline matched to aAah's layout mix
    mix = Counter(g['map'] for g in data['a'])
    marks = ('20', '40', '60', '100', '150', '200')
    print('### T7')
    print('| Dragons; total length after round | ' + ' | '.join(marks) + ' | dragons of 5-8 at 100; 200 | layouts covered at 100; games reaching 200 |')
    print('|---' * (len(marks) + 3) + '|')
    for tag, name in TAGS:
        games = data[tag]
        cells = []
        extra = []
        cov100 = 0
        n200 = 0
        for m in marks:
            by = defaultdict(list)
            for g in games:
                v = g['marks'].get(m)
                if v is not None:
                    by[g['map']].append(v)
            tw = float(sum(mix[k] for k in by if k in mix))
            if not tw:
                cells.append('-')
                continue
            f = lambda j: sum(mix[k] / tw * sum(v[0][j] for v in vs) / len(vs) for k, vs in by.items() if k in mix)
            cells.append('%.1f; %.0f' % (f(0), f(1)))
            if m in ('100', '200'):
                extra.append('%.1f' % f(2))
            if m == '100':
                cov100 = tw / sum(mix.values())
            if m == '200':
                n200 = sum(len(vs) for vs in by.values())
        print('| %s (%d) | ' % (name, len(games)) + ' | '.join(cells) + ' | ' + '; '.join(extra) + ' | %.0f%%; %d |' % (100.0 * cov100, n200))
    # size class big boards
    print('boards above 1,200 cells, dragons; total at 60, 100, 150, 200:')
    for tag, name in TAGS:
        sel = [g for g in data[tag] if g['w'] * g['h'] > 1200]
        out = []
        for m in ('60', '100', '150', '200'):
            vs = [g['marks'][m] for g in sel if m in g['marks']]
            if vs:
                out.append('%.1f; %.0f' % (sum(v[0][0] for v in vs) / len(vs), sum(v[0][1] for v in vs) / len(vs)))
        print('   %s (%d): ' % (name, len(sel)) + ' | '.join(out))
    # splits by round band and count class, aAah and B7Q
    for tag in ('a', 'q'):
        games = data[tag]
        n = len(games)
        S = [s for g in games for s in g['splits']]
        print('### T2', tag)
        for bn, lo, hi in (('0-20', 0, 20), ('21-60', 21, 60), ('61-150', 61, 150), ('151-300', 151, 300), ('301+', 301, 999)):
            sel = [s for s in S if lo <= s[0] <= hi]
            m = max(1, len(sel))
            print('| rounds %s | %.1f | %s | %s | %s | %s | %s | %s | %.2f; %.2f; %.2f |' % (bn, len(sel) / n, f0(sum(1 for s in sel if s[2] == 4), m), f0(sum(1 for s in sel if 5 <= s[2] <= 8), m), f0(sum(1 for s in sel if s[2] >= 9), m),
                  f0(sum(1 for s in sel if s[8] == 0), m), f0(sum(1 for s in sel if s[2] > 4 and s[3] == 2 and s[4] > 2), m), f0(sum(1 for s in sel if s[2] > 4 and s[4] == 2), m),
                  sum(s[2] for s in sel) / m, sum(s[3] for s in sel) / m, sum(s[4] for s in sel) / m))
        for an, lo, hi in (('under 16', 0, 15), ('16-31', 16, 31), ('32-43', 32, 43), ('44-55', 44, 55), ('56-63', 56, 63)):
            sel = [s for s in S if lo <= s[5] <= hi]
            m = max(1, len(sel))
            print('| %s own dragons | %.1f | %s | %s | %s | %s | %s | %s | %.2f; %.2f; %.2f |' % (an, len(sel) / n, f0(sum(1 for s in sel if s[2] == 4), m), f0(sum(1 for s in sel if 5 <= s[2] <= 8), m), f0(sum(1 for s in sel if s[2] >= 9), m),
                  f0(sum(1 for s in sel if s[8] == 0), m), f0(sum(1 for s in sel if s[2] > 4 and s[3] == 2 and s[4] > 2), m), f0(sum(1 for s in sel if s[2] > 4 and s[4] == 2), m),
                  sum(s[2] for s in sel) / m, sum(s[3] for s in sel) / m, sum(s[4] for s in sel) / m))


main()

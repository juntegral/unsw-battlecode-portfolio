"""Scratch (diag-aahsplit): split tables and split hazard from as_scan-<tag>.jsonl.
Usage: python3 as_split.py <tag> [section ...]"""
import sys
import json
from collections import Counter, defaultdict
from pathlib import Path

WORKREL = 'data/analysis/ladder/dossier/work/'
BN = ('0-20', '21-60', '61-150', '151-300', '301+')
# row: 0 rnd 1 id 2 L 3 alive 4 isq 5 lng 6 fh 7 ft 8 ed 9 edt 10 pd 11 n3 12 oh 13 len_since 14 pearls_since 15 age 16 act 17 n 18 eats 19 died+1
# split: 0 rnd 1 parent 2 Lb 3 child 4 after 5 alive 6 isq 7 lng 8 fh 9 ft 10 ed 11 edt 12 pd 13 n3 14 oh 15 len_since 16 pearls_since 17 age 18 keeps 19 tailhead 20 pdead3 21 cdead3


def band(r):
    return 0 if r <= 20 else 1 if r <= 60 else 2 if r <= 150 else 3 if r <= 300 else 4


def ab(n):
    return 0 if n < 8 else 1 if n < 16 else 2 if n < 32 else 3 if n < 48 else 4 if n < 60 else 5


AN = ('<8', '8-15', '16-31', '32-47', '48-59', '60+')


def load(tag):
    return [json.loads(x) for x in Path(WORKREL + 'as_scan-' + tag + '.jsonl').read_text().splitlines() if x]


def pct(a, b):
    return '%5.1f' % (100.0 * a / b) if b else '    -'


def tab(title, rowsd, cols, fmt=None):
    print(title)
    print('   %-14s' % '' + ' '.join('%9s' % str(c) for c in cols))
    for name, vals in rowsd:
        print('   %-14s' % name + ' '.join('%9s' % v for v in vals))


def main():
    tag = sys.argv[1]
    secs = sys.argv[2:] or ['shape', 'haz']
    games = load(tag)
    print('tag', tag, 'games', len(games), 'won', sum(1 for g in games if g['won'] == 1))
    S = [s + [g['gid']] for g in games for s in g['splits']]
    R = [r for g in games for r in g['rows']]
    print('splits', len(S), 'per game %.1f' % (len(S) / len(games)), ' turns at 4+', len(R))
    if 'shape' in secs:
        c = Counter()
        for s in S:
            L = min(s[2], 9)
            shape = 'k2' if s[4] == 2 and s[3] > 2 else 'c2' if s[3] == 2 and s[4] > 2 else '2+2' if s[2] == 4 else 'mid'
            c[L, shape] += 1
            c['b', band(s[0]), L, shape] += 1
            c['a', ab(s[5]), L, shape] += 1
            c['q', s[6], L, shape] += 1
            c['fh', min(s[8], 1), L, shape] += 1
        tot = len(S)
        print('SHAPE of all splits, %% of splits (parent before: 2+2 at 4; c2 = child of 2 leaves, parent keeps L-2; k2 = parent keeps 2, child L-2; mid = other)')
        for L in range(4, 10):
            print('   L=%s%s  ' % (L, '+' if L == 9 else ' ') + '  '.join('%s %s' % (sh, pct(c[L, sh], tot)) for sh in ('2+2', 'c2', 'k2', 'mid')))
        for nm, key, names in (('round band', 'b', BN), ('alive', 'a', AN), ('queen', 'q', ('no', 'yes')), ('free tile at head', 'fh', ('none', 'some'))):
            print(' by ' + nm + ': share of that group''s splits')
            for z, n in enumerate(names):
                t = sum(v for k2, v in c.items() if len(k2) == 4 and k2[0] == key and k2[1] == z)
                if not t:
                    continue
                p4 = sum(v for k2, v in c.items() if len(k2) == 4 and k2[0] == key and k2[1] == z and k2[2] == 4)
                c2 = sum(v for k2, v in c.items() if len(k2) == 4 and k2[0] == key and k2[1] == z and k2[3] == 'c2')
                k2n = sum(v for k2, v in c.items() if len(k2) == 4 and k2[0] == key and k2[1] == z and k2[3] == 'k2')
                md = sum(v for k2, v in c.items() if len(k2) == 4 and k2[0] == key and k2[1] == z and k2[3] == 'mid')
                print('   %-8s n=%6d (%.1f a game)  at 4: %s  child 2 off a longer: %s  keeps 2: %s  other: %s' % (n, t, t / len(games), pct(p4, t), pct(c2, t), pct(k2n, t), pct(md, t)))
        # by parent length exact: child size distribution
        d = defaultdict(Counter)
        for s in S:
            d[min(s[2], 12)][s[3] if s[3] <= 2 else ('L-2' if s[4] == 2 else 'L-3' if s[4] == 3 else 'other')] += 1
        print(' child size by parent length (count):')
        for L in sorted(d):
            print('   L=%2d n=%6d  ' % (L, sum(d[L].values())) + '  '.join('%s: %d' % (k, v) for k, v in sorted(d[L].items(), key=lambda kv: str(kv[0]))))
        # free head and death after
        for shape_name, f in (('2+2 at 4', lambda s: s[2] == 4), ('child 2 off 5+', lambda s: s[2] > 4 and s[3] == 2), ('keeps 2 (child L-2), 5+', lambda s: s[2] > 4 and s[4] == 2)):
            sel = [s for s in S if f(s)]
            if not sel:
                continue
            n = len(sel)
            print(' %-26s n=%6d  no free tile at head %s  ft=0 %s  enemy head<=3 of head %s  of tail %s  parent dead in 3 rounds %s  child dead %s  pearl<=3 %s' % (
                shape_name, n, pct(sum(1 for s in sel if s[8] == 0), n), pct(sum(1 for s in sel if s[9] == 0), n),
                pct(sum(1 for s in sel if s[10] <= 3), n), pct(sum(1 for s in sel if s[11] <= 3), n),
                pct(sum(1 for s in sel if s[20]), n), pct(sum(1 for s in sel if s[21]), n), pct(sum(1 for s in sel if s[12] <= 3), n)))
    if 'haz' in secs:
        print('HAZARD: splits per 100 turns of a dragon at that length (turns)')

        def haz(name, keyf, names, filt=lambda r: True):
            c = Counter()
            for r in R:
                if not filt(r):
                    continue
                L = min(r[2], 9)
                k = keyf(r)
                c[k, L, 't'] += 1
                c[k, L, 's'] += int(r[16] >= 2)
            print(' by ' + name)
            for z, n in enumerate(names):
                print('   %-10s' % n + '  '.join('L%d%s %s (%d)' % (L, '+' if L == 9 else '', pct(c[z, L, 's'], c[z, L, 't']), c[z, L, 't']) for L in range(4, 10)))
        haz('all', lambda r: 0, ('all',))
        haz('queen', lambda r: r[4], ('no', 'yes'))
        nq = lambda r: not r[4]
        haz('free tiles at head (not queen)', lambda r: min(r[6], 3), ('0', '1', '2', '3'), nq)
        op = lambda r: not r[4] and r[6] > 0
        haz('round band (not queen, head free)', lambda r: band(r[0]), BN, op)
        haz('alive (not queen, head free)', lambda r: ab(r[3]), AN, op)
        haz('turns at this length (not queen, head free)', lambda r: min(r[13], 5), ('0', '1', '2', '3', '4', '5+'), op)
        haz('pearl steps (not queen, head free)', lambda r: 0 if r[10] == 1 else 1 if r[10] <= 3 else 2 if r[10] <= 6 else 3, ('1', '2-3', '4-6', 'none'), op)
        haz('enemy head dist (not queen, head free)', lambda r: 0 if r[8] <= 2 else 1 if r[8] <= 4 else 2 if r[8] <= 8 else 3, ('<=2', '3-4', '5-8', '9+'), op)
        haz('free tiles at tail (not queen, head free)', lambda r: min(r[7], 3), ('0', '1', '2', '3'), op)
        haz('own heads within 3 (not queen, head free)', lambda r: min(r[12], 3), ('0', '1', '2', '3+'), op)
        haz('longest of side (not queen, head free)', lambda r: r[5], ('no', 'tie', 'sole'), op)


main()

"""Scratch (diag-aahsplit): which end leaves when a boxed head splits, by what stands beside the head.
Usage: python3 as_boxagg.py <tag> [<tag> ...]"""
import sys
import json
from collections import Counter
from pathlib import Path

WORKREL = 'data/analysis/ladder/dossier/work/'
# row: 0 rnd 1 id 2 L 3 alive 4 isq 5 child size (0 none) 6 died+1 7 sides [[type 0 kelp 1 own 2 mate 3 enemy, index from the tail tip, length]] 8 parent dead in 3 rounds 9 child dead


def klass(r):
    sides = r[7]
    L = r[2]
    own = [s for s in sides if s[0] == 1 and s[1] != L - 2]        # the neck is always there
    oth = [s for s in sides if s[0] in (2, 3)]
    if oth:
        j = min(s[1] for s in oth)
        who = 'mate' if any(s[0] == 2 and s[1] == j for s in oth) else 'enemy'
        return 'A another dragon, soonest part %s from its tail tip (%s)' % ('0' if j == 0 else '1' if j == 1 else '2-3' if j <= 3 else '4+', who)
    if own:
        j = min(s[1] for s in own)
        return 'B own body and kelp only, own part %s from the tail tip' % ('0-1' if j <= 1 else '2+')
    return 'C kelp only'


def main():
    for tag in sys.argv[1:]:
        games = [json.loads(x) for x in Path(WORKREL + 'as_box-' + tag + '.jsonl').read_text().splitlines() if x]
        n = len(games)
        R = [r for g in games for r in g['rows'] if r[3] < 64]
        print('%s: %d games, boxed turns at 4+ under 64 dragons: %d (%.1f a game)' % (tag, n, len(R), len(R) / n))
        for nm, f in (('length 4', lambda r: r[2] == 4), ('length 5', lambda r: r[2] == 5), ('length 6+', lambda r: r[2] >= 6)):
            c = Counter()
            for r in R:
                if not f(r):
                    continue
                k = klass(r)
                L = r[2]
                act = 'no split' if r[5] == 0 else 'child 2' if (r[5] == 2 and L > 4) else 'keeps 2' if r[5] == L - 2 else 'other'
                if L == 4 and r[5] == 2:
                    act = 'keeps 2'
                c[k, act] += 1
                c[k, 't'] += 1
                if act in ('child 2', 'keeps 2'):
                    c[k, act, 'pdead'] += r[8]
                    c[k, act, 'cdead'] += r[9]
            print('  ' + nm)
            for k in sorted(set(x[0] for x in c)):
                t = c[k, 't']
                line = '    %-46s %6d (%.1f a game): ' % (k, t, t / n)
                for act in ('child 2', 'keeps 2', 'no split'):
                    line += '%s %.0f%%' % (act, 100.0 * c[k, act] / t)
                    if act != 'no split' and c[k, act]:
                        line += ' [front dead in 3 rounds %.0f%%, rear %.0f%%]' % (100.0 * c[k, act, 'pdead'] / c[k, act], 100.0 * c[k, act, 'cdead'] / c[k, act])
                    line += '; '
                print(line)


main()

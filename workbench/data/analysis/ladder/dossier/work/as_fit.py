"""Scratch (diag-aahsplit): how well a coded split rule predicts the split turns of a side.
Usage: python3 as_fit.py <tag> [<tag> ...]
Rule A(N): boxed head (no free tile beside it) -> split; else under N own dragons, no pearl beside the head, a free tile beside the tail -> split; else move.
Rule OURS: boxed -> split; under 60 dragons and (length 4, or longer before the grow round: 300 up to 1,200 cells, 150 above) -> split."""
import sys
import json
from collections import Counter
from pathlib import Path

WORKREL = 'data/analysis/ladder/dossier/work/'


def rule_a(g, r, N, strict):
    if r[3] >= 64:
        return False
    if r[6] == 0:
        return True
    if r[4]:
        return r[2] == 4 and r[10] != 1 and r[7] > 0 if strict else False
    if r[3] < N and r[10] != 1 and r[7] > 0:
        return True
    return False


def rule_ours(g, r):
    if r[3] >= 64:
        return False
    if r[6] == 0:
        return True
    if r[4]:
        return False
    grow = 300 if g['w'] * g['h'] <= 1200 else 150
    return r[3] < 60 and (r[2] == 4 or r[0] <= grow)


def main():
    for tag in sys.argv[1:]:
        games = [json.loads(x) for x in Path(WORKREL + 'as_scan-' + tag + '.jsonl').read_text().splitlines() if x]
        n = len(games)
        rows = [(g, r) for g in games for r in g['rows']]
        tot = len(rows)
        sp = sum(1 for g, r in rows if r[16] >= 2)
        print('%s: %d games, %d turns at 4+ (%.0f a game), %d splits (%.1f a game)' % (tag, n, tot, tot / n, sp, sp / n))
        print('   rule                 says split  and it does (precision)   splits foreseen (recall)   split turns the rule forbids a game   turns it adds a game')
        for name, f in [('A(%d)' % N, lambda g, r, N=N: rule_a(g, r, N, False)) for N in (40, 44, 48, 50, 52, 56, 60)] + [('OURS', rule_ours), ('boxed only', lambda g, r: r[6] == 0 and r[3] < 64)]:
            c = Counter()
            for g, r in rows:
                c[f(g, r), r[16] >= 2] += 1
            says = c[True, True] + c[True, False]
            print('   %-18s %9d   %5.1f%%                    %5.1f%%                     %7.1f                             %7.1f' % (
                name, says, 100.0 * c[True, True] / max(1, says), 100.0 * c[True, True] / max(1, sp), c[False, True] / n, c[True, False] / n))
        # by part, rule A(48)
        c = Counter()
        for g, r in rows:
            part = 'cap 64' if r[3] >= 64 else 'boxed' if r[6] == 0 else 'queen' if r[4] else 'pearl beside' if r[10] == 1 else 'under 44' if r[3] < 44 else '44-55' if r[3] < 56 else '56-63'
            c[part, 't'] += 1
            c[part, 's'] += int(r[16] >= 2)
        print('   by part: ' + '; '.join('%s %d turns a game, split on %.1f%%' % (p, c[p, 't'] / n, 100.0 * c[p, 's'] / c[p, 't']) for p in ('boxed', 'queen', 'pearl beside', 'under 44', '44-55', '56-63', 'cap 64') if c[p, 't']))


main()

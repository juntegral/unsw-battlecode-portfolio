"""Scratch (diag-aahsplit): what a dragon of 4 or longer does between splits: visits at each length, how they end,
and whole spells from reaching 4 to the next split, death or game end.
Usage: python3 as_dwell.py <tag> [<tag> ...]"""
import sys
import json
from collections import Counter, defaultdict
from pathlib import Path

WORKREL = 'data/analysis/ladder/dossier/work/'


def med(v):
    v = sorted(v)
    return v[len(v) // 2] if v else 0


def main():
    for tag in sys.argv[1:]:
        games = [json.loads(x) for x in Path(WORKREL + 'as_scan-' + tag + '.jsonl').read_text().splitlines() if x]
        visits = defaultdict(list)      # (L, regime) -> [turns]
        ends = Counter()
        spells = []                     # (peak length, turns, pearls, end)
        for g in games:
            by = defaultdict(list)
            for r in g['rows']:
                if not r[4]:
                    by[r[1]].append(r)
            for i, rs in by.items():
                start = 0
                sp_start = 0
                for z, r in enumerate(rs):
                    last = z + 1 == len(rs)
                    nxt = None if last else rs[z + 1]
                    contiguous = nxt is not None and nxt[0] - r[0] <= 1
                    L = r[2]
                    if r[16] >= 2:
                        end = 'split boxed' if r[6] == 0 else 'split free'
                    elif r[19]:
                        end = 'dies'
                    elif nxt is None or not contiguous:
                        end = 'drops under 4 or game ends'
                    elif nxt[2] > L:
                        end = 'eats'
                    elif nxt[2] < L:
                        end = 'pays a step'
                    else:
                        end = None
                    if end:
                        Lc = min(L, 9)
                        regime = 'full' if rs[start][3] >= 56 else 'mid' if rs[start][3] >= 44 else 'open'
                        visits[Lc, regime].append(z - start + 1)
                        ends[Lc, regime, end] += 1
                        start = z + 1
                    if r[16] >= 2 or r[19] or nxt is None or not contiguous:
                        seg = rs[sp_start:z + 1]
                        spells.append((max(x[2] for x in seg), len(seg), sum(x[18] for x in seg), 'split' if r[16] >= 2 else 'dies' if r[19] else 'other', seg[0][3]))
                        sp_start = z + 1
        print('%s (%d games): visits at a length (not queen), by own dragons alive when the visit starts: open <44, mid 44-55, full 56+' % (tag, len(games)))
        for regime in ('open', 'mid', 'full'):
            print('  ' + regime)
            for L in range(4, 10):
                v = visits[L, regime]
                if not v:
                    continue
                n = len(v)
                es = ('eats', 'split free', 'split boxed', 'dies', 'pays a step', 'drops under 4 or game ends')
                print('    L=%d%s visits %6d  mean %5.1f turns, median %2d, 1 turn %4.1f%%, 10+ turns %4.1f%% | ends: ' % (
                    L, '+' if L == 9 else ' ', n, sum(v) / n, med(v), 100.0 * sum(1 for x in v if x == 1) / n, 100.0 * sum(1 for x in v if x >= 10) / n) +
                    ', '.join('%s %.0f%%' % (e, 100.0 * ends[L, regime, e] / n) for e in es))
        for nm, lo, hi in (('open <44', 0, 43), ('mid 44-55', 44, 55), ('full 56+', 56, 64)):
            sel = [s for s in spells if lo <= s[4] <= hi]
            if not sel:
                continue
            n = len(sel)
            pk = Counter(min(s[0], 9) for s in sel)
            print('  spells from reaching 4+ to the next split or death, started at %s: %d; turns mean %.1f median %d; pearls mean %.2f; end split %.0f%% dies %.0f%%; peak length ' % (
                nm, n, sum(s[1] for s in sel) / n, med([s[1] for s in sel]), sum(s[2] for s in sel) / n,
                100.0 * sum(1 for s in sel if s[3] == 'split') / n, 100.0 * sum(1 for s in sel if s[3] == 'dies') / n) +
                ' '.join('%d%s: %.0f%%' % (L, '+' if L == 9 else '', 100.0 * pk[L] / n) for L in range(4, 10)))


main()

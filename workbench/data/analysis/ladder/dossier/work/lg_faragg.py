"""Scratch (diag-longest): tables from lg_far-*.jsonl. python3 lg_faragg.py [race]"""
import sys
import json
from pathlib import Path
from statistics import mean, median

WORK = Path('data/analysis/ladder/dossier/work')
ARMS = dict(MAIN=('m1', 'm2', 'm3'), B7=('b1', 'b2'), B7Q=('q1',))


def load(tags):
    out = []
    for t in tags:
        p = WORK / ('lg_far-%s.jsonl' % t)
        if p.exists():
            out += [json.loads(l) for l in p.read_text().splitlines() if l]
    return out


def table(name, G, s):
    print('== %s: %d games' % (name, len(G)))
    for size, lo, hi in (('up to 1200 cells', 0, 1200), ('above 1200 cells', 1201, 99999)):
        V = [g for g in G if lo <= g['cells'] <= hi and g['last'] >= 499]
        if not V:
            continue
        print('  %s, %d full games' % (size, len(V)))
        for r in ('300', '400', '450', '499'):
            rows = [g['marks'][r][s] for g in V if r in g['marks'] and g['marks'][r][s]]
            if not rows:
                continue
            k = len(rows)
            m = [sum(x[z] for x in rows) / k for z in range(19)]
            oth = m[2] - m[0]
            may = [m[4], m[8], m[12], m[16]]
            big = [m[6], m[10], m[14], m[18]]
            cnt = [m[3] + m[5], m[7] + m[9], m[11] + m[13], m[15] + m[17]]
            print('    r%s n%d: longest %.1f, alive %.1f, total %.1f | other length %.1f = may feed: within 5 %.1f, 6-15 %.1f, 16-30 %.1f, 31+ %.1f; too long: %.1f %.1f %.1f %.1f | dragons by band %.1f %.1f %.1f %.1f' % (
                r, k, m[0], m[1], m[2], oth, may[0], may[1], may[2], may[3], big[0], big[1], big[2], big[3], cnt[0], cnt[1], cnt[2], cnt[3]))
    for b0, b1 in ((200, 299), (300, 399), (400, 499)):
        F = [f for g in G for f in g['feeds'] if f[1] == s and b0 <= f[0] <= b1]
        if not F:
            continue
        n = len(F)
        print('  by-choice deaths r%d-%d: %.1f a game, length mean %.2f (2: %d%%, 3: %d%%, 4-5: %d%%, 6+: %d%%); a mate twice as long within 3 tiles %d%%, within 4-10 %d%%, none within 10 %d%%; that mate is the longest %d%%; within 3 of the longest %d%%; an enemy head within 4 %d%%; mate length median %d' % (
            b0, b1, n / len(G), mean(f[2] for f in F), 100 * sum(f[2] == 2 for f in F) // n, 100 * sum(f[2] == 3 for f in F) // n,
            100 * sum(4 <= f[2] <= 5 for f in F) // n, 100 * sum(f[2] >= 6 for f in F) // n,
            100 * sum(f[3] <= 3 for f in F) // n, 100 * sum(3 < f[3] <= 10 for f in F) // n, 100 * sum(f[3] > 10 for f in F) // n,
            100 * sum(f[3] <= 10 and f[5] for f in F) // n, 100 * sum(f[6] <= 3 for f in F) // n, 100 * sum(f[8] > 0 for f in F) // n,
            median([f[4] for f in F if f[3] <= 10] or [0])))


def main():
    allg = []
    for arm, tags in ARMS.items():
        G = load(tags)
        allg += G
        if G:
            table('ours ' + arm, G, 0)
    for opp in sorted(set(g['opp'] for g in allg if g['opp'])):
        table('theirs ' + opp, [g for g in allg if g['opp'] == opp], 1)
    T = load(('T',))
    if T:
        table('rank-1 (every tenth game)', T, 0)


main()

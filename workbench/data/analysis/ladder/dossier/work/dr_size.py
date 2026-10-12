# Scratch (diag-drops): the drop tables and the second view split by layout size (above 1200 cells or not) and, for drops,
# by the round of the death (101-150, 151-300). Layout-equal means inside each size group.
# Usage: python3 data/analysis/ladder/dossier/work/dr_size.py
import sys, json
sys.dont_write_bytecode = True
from collections import defaultdict, Counter

BASE = 'data/analysis/ladder/dossier/work/'
FILES = ['dr_scan-O0.jsonl', 'dr_scan-O1.jsonl', 'dr_scan-O2.jsonl', 'dr_scan-R0.jsonl', 'dr_scan-R1.jsonl', 'dr_scan-R2.jsonl']
ACTORS = ('O', 'R', 'OO', 'RO')


def actor(who, x):
    return who if x == 0 else who + 'O'


def lm(tab, num, den):
    vals = [tab[l][num] / tab[l][den] for l in tab if tab[l][den]]
    return 100 * sum(vals) / len(vals) if vals else float('nan')


def mclass(m):
    if m // 256 % 2:
        return 'feeding'
    if m // 64 % 2:
        return 'zone'
    if m // 4 % 2:
        return 'pocket'
    if m // 16 % 2:
        return 'no room'
    if m // 8 % 2:
        return 'threat'
    if m % 2:
        return 'enemy beside'
    if m // 2 % 2:
        return 'mate beside'
    if m // 32 % 2:
        return 'tight'
    return 'nothing'


def main():
    drop = defaultdict(lambda: defaultdict(Counter))
    adj = defaultdict(lambda: defaultdict(Counter))
    wat = defaultdict(lambda: defaultdict(Counter))
    games = defaultdict(set)
    for name in FILES:
        with open(BASE + name) as f:
            for line in f:
                if not line.strip():
                    continue
                gm = json.loads(line)
                who, lay = gm['who'], gm['layout']
                size = 'big' if gm['cells'] > 1200 else 'small'
                games[(who, size)].add(lay)
                for d in gm['deaths']:
                    if d[0] < 101:
                        continue
                    ph = '101-150' if d[0] <= 150 else '151-300'
                    for x in (0, 1):
                        a = actor(who, x)
                        own = d[2] == x
                        for key in ((a, size, ph), (a, size, '101-300')):
                            c = drop[key][lay]
                            for pr in d[12]:
                                mine, theirs = pr[1 + x], pr[2 - x]
                                ate = pr[7] == x
                                none = pr[7] == -1
                                c['n'] += 1
                                c['e'] += ate
                                c['own'] += own
                                if own:
                                    c['own_n'] += 1
                                    c['own_e'] += ate
                                if theirs > 5 and mine <= 5:
                                    cls = 'a' if mine <= 2 else 'b'
                                    c[cls + '_n'] += 1
                                    c[cls + '_e'] += ate
                                    c[cls + '_none'] += none
                                    if ate:
                                        c[cls + '_w'] += pr[8]
                                        c[cls + '_big'] += pr[9] >= 5
                            w = d[13 + x]
                            if w is not None and min(pr[2 - x] for pr in d[12]) > 5 and w[6]:
                                wc = wat[key][lay]
                                k = 'd1' if w[1] == 1 else 'd2' if w[1] == 2 else 'd3'
                                wc[k] += 1
                                first = w[6][1]
                                wc[k + '_E'] += first == 'E'
                                wc[k + '_T'] += first in 'Tt'
                                wc[k + '_A'] += first in 'AaPp'
                                wc[k + '_S'] += first == 'S'
                                wc[k + '_X'] += first in 'RWOBMNIUZ'
                                wc[k + '_got'] += 'E' in w[6]
                for s, w, lc, role, nadj, kind, ac, m, did, after, n in gm['adj']:
                    if w != 1:
                        continue
                    a = actor(who, s)
                    c = adj[(a, size)][lay]
                    mc = mclass(m)
                    c['n'] += n
                    c['miss'] += n if did else 0
                    c[mc] += n
                    c[mc + '_miss'] += n if did else 0
                    if lc <= 1:
                        c['short'] += n
                        c['short_miss'] += n if did else 0
    print('layouts', {k: len(v) for k, v in sorted(games.items())})
    print()
    print('## drops by layout size and round of the death: % eaten by the actor | % of drops that are its own bodies | own bodies eaten %')
    print('   own head within 2, no enemy within 5: share of drops, eaten %, nobody %, wait | own head at 3-5, no enemy within 5: the same')
    for size in ('big', 'small'):
        for ph in ('101-150', '151-300', '101-300'):
            for a in ACTORS:
                t = drop[(a, size, ph)]
                print('%-5s %-8s %-3s | %5.1f | %5.1f | %5.1f | %5.1f %5.1f %5.1f %5.1f | %5.1f %5.1f %5.1f %5.1f | long eater %4.1f %4.1f' % (
                    size, ph, a, lm(t, 'e', 'n'), lm(t, 'own', 'n'), lm(t, 'own_e', 'own_n'),
                    lm(t, 'a_n', 'n'), lm(t, 'a_e', 'a_n'), lm(t, 'a_none', 'a_n'), lm(t, 'a_w', 'a_e') / 100,
                    lm(t, 'b_n', 'n'), lm(t, 'b_e', 'b_n'), lm(t, 'b_none', 'b_n'), lm(t, 'b_w', 'b_e') / 100,
                    lm(t, 'a_big', 'a_e'), lm(t, 'b_big', 'b_e')))
    print()
    print('## watcher of a drop with no enemy head within 5, first turn: eats / nearer / farther or as far / splits / dies, and ate one within 6 turns')
    for size in ('big', 'small'):
        for ph in ('101-150', '151-300'):
            for k, kn in (('d1', '1 step'), ('d2', '2 steps'), ('d3', '3-5 steps')):
                for a in ACTORS:
                    t = wat[(a, size, ph)]
                    print('%-5s %-8s %-9s %-3s | %5.1f %5.1f %5.1f %5.1f %5.1f | %5.1f | n %d' % (
                        size, ph, kn, a, lm(t, k + '_E', k), lm(t, k + '_T', k), lm(t, k + '_A', k), lm(t, k + '_S', k), lm(t, k + '_X', k),
                        lm(t, k + '_got', k), sum(t[l][k] for l in t)))
    print()
    print('## second view by layout size, rounds 101-300: not taken %, length 2-3 not taken %, then per class: share of turns, not taken %')
    names = ('zone', 'feeding', 'pocket', 'no room', 'tight', 'threat', 'mate beside', 'nothing')
    for size in ('big', 'small'):
        for a in ACTORS:
            t = adj[(a, size)]
            line = '%-5s %-3s | %5.1f | %5.1f |' % (size, a, lm(t, 'miss', 'n'), lm(t, 'short_miss', 'short'))
            for mc in names:
                line += ' %s %4.1f %4.1f |' % (mc, lm(t, mc, 'n'), lm(t, mc + '_miss', mc))
            print(line)
    print()
    print('## second view, per layout: not taken % ours / rank-1; zone class share and not taken %')
    lays = sorted({l for k in adj for l in adj[k]})
    for l in lays:
        row = l.ljust(22)
        for a in ACTORS:
            for size in ('big', 'small'):
                t = adj[(a, size)]
                if l in t and t[l]['n']:
                    c = t[l]
                    row += ' | %s %s %5.1f zone %4.1f %5.1f' % (a, size, 100 * c['miss'] / c['n'], 100 * c['zone'] / c['n'], 100 * c['zone_miss'] / max(1, c['zone']))
        print(row)
    print()
    print('## drops per layout, rounds 101-300: eaten % ours / rank-1 / opponents')
    for l in lays:
        row = l.ljust(22)
        for a in ACTORS:
            for size in ('big', 'small'):
                t = drop[(a, size, '101-300')]
                if l in t and t[l]['n']:
                    c = t[l]
                    row += ' | %s %5.1f own %4.1f' % (a, 100 * c['e'] / c['n'], 100 * c['own'] / c['n'])
        print(row)


main()

"""Scratch (diag-longest): compact tables from lg_scan-*.jsonl.
Usage: python3 lg_agg2.py opp [online|ladder|top1]   growth of the longest per 100 rounds, both sides
       python3 lg_agg2.py gap [online|ladder]        lost race games: gap at the end, our peak, how the peak was lost
       python3 lg_agg2.py start [online|ladder]      our first by-choice death round against the final longest"""
import sys
import json
from pathlib import Path
from statistics import median, mean
from collections import Counter, defaultdict

WORK = Path('data/analysis/ladder/dossier/work')
ARMS = dict(MAIN=('m1', 'm2', 'm3'), B7=('b1', 'b2'), B7Q=('q1', 'q2'))
MARKS = (100, 200, 300, 400, 499)
CAUSE = ('wall', 'own body', 'body', 'rammed it', 'was rammed', 'unpaid', 'bad split', 'no action')


def load(tags):
    out = []
    for t in tags:
        p = WORK / ('lg_scan-%s.jsonl' % t)
        if p.exists():
            for l in p.read_text().splitlines():
                if l:
                    out.append(json.loads(l))
    return out


def at(g, r, k):
    s = g['snaps']
    return s[min(r, len(s) - 1)][k]


def in_race(g):
    return g['decided'] in ('longest', 'total') or (g['decided'] == 'elimination' and g['qdeath'][0] is not None and g['qdeath'][1] is not None)


def groups(mode):
    if mode == 'online':
        out = []
        for arm, tags in ARMS.items():
            G = load(tags)
            if G:
                out.append(('ours ' + arm, G, 0))
        allg = load(sum(ARMS.values(), ()))
        for opp in sorted(set(g['opp'] for g in allg)):
            out.append(('theirs ' + opp, [g for g in allg if g['opp'] == opp], 1))
        return out
    if mode == 'ladder':
        G = load(('L0', 'L1'))
        return [('ours ladder', G, 0), ('ladder opponents', G, 1)]
    G = load(('T0', 'T1'))
    return [('rank-1', G, 0), ('rank-1 opponents', G, 1)]


def opp(mode):
    for name, G, s in groups(mode):
        print('== %s: %d games | longest mean (median) at %s | second %s | alive %s' % (
            name, len(G), ' '.join('%.1f(%d)' % (mean(at(g, m, s) for g in G), median(at(g, m, s) for g in G)) for m in MARKS),
            ' '.join('%.1f' % mean(at(g, m, 2 + s) for g in G) for m in MARKS), ' '.join('%.0f' % mean(at(g, m, 4 + s) for g in G) for m in MARKS)))
        for bk in range(5):
            reach = [g for g in G if g['last'] >= bk * 100]
            k = len(reach)
            if not k:
                continue
            lec = [sum(1 for g in reach for e in g['roundeat'] if e[1] == s and e[0] // 100 == bk and e[4] >= 8 and e[2] == c) / k for c in range(4)]
            dl = sum(g['deaths'][s][bk][9] for g in reach) / k
            dp = sum(g['deaths'][s][bk][10] for g in reach) / k
            nd = sum(1 for g in reach for f in g['feeds'] if f[1] == s and f[0] // 100 == bk and f[8]) / k
            near = sum(1 for g in reach for f in g['feeds'] if f[1] == s and f[0] // 100 == bk and f[8] and f[3] <= 3 and f[4] >= 8) / k
            ff = [sum(g['feedfate'][s][bk][c] for g in reach) / k for c in range(5)]
            gain = mean(at(g, min(bk * 100 + 99, 499), s) - at(g, bk * 100, s) for g in reach)
            tsp = sum(1 for g in reach for t in g['tsplits'] if t[1] == s and t[0] // 100 == bk and t[2] >= 8) / k
            tde = sum(1 for g in reach for d in g['tdeaths'] if d['s'] == s and d['r'] // 100 == bk and d['L'] >= 8) / k
            tdl = sum(d['L'] for g in reach for d in g['tdeaths'] if d['s'] == s and d['r'] // 100 == bk and d['L'] >= 8) / k
            print('  r%d+ n%d: longest %+.1f | top8+ eats nat %.1f fed %.1f own %.1f opp %.1f | by-choice deaths %.1f len %.1f pearls %.1f (beside top8+ %.1f) > top %.1f long %.1f short %.1f enemy %.1f none %.1f | top8+ splits %.2f deaths %.2f (len %.1f)' % (
                bk * 100, k, gain, lec[0], lec[1], lec[2], lec[3], nd, dl, dp, near, ff[0], ff[1], ff[2], ff[3], ff[4], tsp, tde, tdl))
        tot = [sum(g['lt'][s][b][z] for g in G for b in range(5)) for z in range(14)]
        if tot[0]:
            print('  top8+ turns %d: ended in a true ring %.2f%% (clean tile existed %.2f%%), in a ring in view %.2f%% (clean %.2f%%), no clean tile %.2f%%, rammed before next turn %.2f%%' % (
                tot[0], 100.0 * tot[2] / tot[0], 100.0 * tot[3] / tot[0], 100.0 * tot[6] / tot[0], 100.0 * tot[7] / tot[0], 100.0 * tot[10] / tot[0], 100.0 * tot[13] / tot[0]))


def peak(g, s, after=150):
    best, br = 0, 0
    for r, sn in enumerate(g['snaps']):
        if r >= after and sn[s] > best:
            best, br = sn[s], r
    return best, br


def gap(mode):
    sets = [(arm, load(tags)) for arm, tags in ARMS.items()] if mode == 'online' else [('ladder', load(('L0', 'L1')))]
    for arm, G in sets:
        if not G:
            continue
        race = [g for g in G if in_race(g)]
        lost = [g for g in race if not g['win']]
        won = [g for g in race if g['win']]
        print('== %s: %d games, race %d, won %d, lost %d' % (arm, len(G), len(race), len(won), len(lost)))
        cls = Counter()
        rows = []
        for g in lost:
            of, tf = g['final'][0], g['final'][1]
            pk, pr = peak(g, 0)
            had = pk > tf
            big = [d for d in g['tdeaths'] if d['s'] == 0 and d['L'] >= 8]
            dec = [d for d in big if d['L'] > tf]
            sp = [t for t in g['tsplits'] if t[1] == 0 and t[2] > tf and t[3] <= tf and t[4] <= tf]
            if g['decided'] == 'elimination':
                c = 'wiped out'
            elif dec:
                d = dec[-1]
                code = (0, 1, 2, 3 if d['own'] else 4, 5 + (d['act'] if d['act'] is not None else 2))[min(d['reason'], 4)]
                c = 'top longer than their final died: ' + CAUSE[code]
            elif sp:
                c = 'top longer than their final split below it'
            elif had:
                c = 'peak above their final, lost otherwise'
            else:
                c = 'never above their final'
            cls[c] += 1
            rows.append((g['game'], g['map'], g['opp'][:3] if g['opp'] else str(g.get('rating')), g['cells'], of, tf, pk, pr, at(g, pr, 1), c,
                         ['r%d L%d' % (d['r'], d['L']) for d in big][-4:]))
        for c, n in cls.most_common():
            print('   %3d  %s' % (n, c))
        gaps = sorted(g['final'][1] - g['final'][0] for g in lost if g['decided'] != 'elimination')
        if gaps:
            print('   end gap (theirs - ours), lost and not wiped: n %d median %d; within 3: %d, 4-10: %d, 11-20: %d, 21-40: %d, over 40: %d' % (
                len(gaps), median(gaps), sum(1 for x in gaps if x <= 3), sum(1 for x in gaps if 3 < x <= 10), sum(1 for x in gaps if 10 < x <= 20),
                sum(1 for x in gaps if 20 < x <= 40), sum(1 for x in gaps if x > 40)))
        wg = sorted(g['final'][0] - g['final'][1] for g in won if g['decided'] != 'elimination')
        if wg:
            print('   won margin (ours - theirs), not by elimination: n %d median %d; within 3: %d, 4-10: %d, 11-20: %d, over 20: %d' % (
                len(wg), median(wg), sum(1 for x in wg if x <= 3), sum(1 for x in wg if 3 < x <= 10), sum(1 for x in wg if 10 < x <= 20), sum(1 for x in wg if x > 20)))
        if mode == 'online':
            for r in sorted(rows, key=lambda r: (r[2], r[0])):
                print('   %d %s %s %d: end %d/%d, our peak %d at r%d (theirs then %d): %s %s' % r)


def start(mode):
    sets = [(arm, load(tags)) for arm, tags in ARMS.items()] if mode == 'online' else [('ladder', load(('L0', 'L1')))]
    for arm, G in sets:
        if not G:
            continue
        print('== %s' % arm)
        by = defaultdict(list)
        for g in G:
            if g['last'] < 499:
                continue
            fr = [f[0] for f in g['feeds'] if f[1] == 0 and f[8] and f[3] <= 15]
            S = fr[4] if len(fr) >= 5 else None
            k = 'none' if S is None else 'r200-299' if S < 300 else 'r300-399' if S < 400 else 'r400+'
            by[k].append(g)
        for k in ('r200-299', 'r300-399', 'r400+', 'none'):
            V = by[k]
            if not V:
                continue
            race = [g for g in V if in_race(g)]
            print('   fifth by-choice death in %s: %d full games (cells median %d); alive at r200 %.0f r400 %.0f end %.0f; our longest r200 %.1f r300 %.1f r400 %.1f end %.1f (median %d); theirs end %.1f (median %d); race %d won %d' % (
                k, len(V), median(g['cells'] for g in V), mean(at(g, 200, 4) for g in V), mean(at(g, 400, 4) for g in V), mean(g['final'][4] for g in V),
                mean(at(g, 200, 0) for g in V), mean(at(g, 300, 0) for g in V), mean(at(g, 400, 0) for g in V), mean(g['final'][0] for g in V),
                median(g['final'][0] for g in V), mean(g['final'][1] for g in V), median(g['final'][1] for g in V), len(race), sum(g['win'] or 0 for g in race)))


def main():
    what = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'online'
    if what == 'opp':
        opp(mode)
    elif what == 'gap':
        gap(mode)
    elif what == 'start':
        start(mode)


main()

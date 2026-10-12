"""Scratch (diag-longest): the remaining figures of diag-longest.md from lg_scan-*.jsonl.
python3 lg_misc.py size   by-choice death length per century and per 25 rounds, longest, second, alive, total, by map size, every side
python3 lg_misc.py rams   rams on our longest by minimum length: in view, clean tile by ring, decisive and avoidable (online pooled, ladder)
python3 lg_misc.py two    what a halved longest would turn or lose; wins that came from their longest dying
python3 lg_misc.py fate   who eats the pearls of deaths by choice, by arm, size and century
python3 lg_misc.py lost   the lost race games pooled: wiped, never above their final, gaps, totals"""
import sys
import json
from pathlib import Path
from statistics import mean, median

WORK = Path('data/analysis/ladder/dossier/work')
ON = ('m1', 'm2', 'm3', 'b1', 'b2', 'q1')
ARMS = (('MAIN', ('m1', 'm2', 'm3')), ('B7', ('b1', 'b2')), ('B7Q', ('q1',)))


def load(tags):
    out = []
    for t in tags:
        p = WORK / ('lg_scan-%s.jsonl' % t)
        if p.exists():
            out += [json.loads(l) for l in p.read_text().splitlines() if l]
    return out


def at(g, r, k):
    s = g['snaps']
    return s[min(r, len(s) - 1)][k]


def in_race(g):
    return g['decided'] in ('longest', 'total') or (g['decided'] == 'elimination' and g['qdeath'][0] is not None and g['qdeath'][1] is not None)


def size():
    def hist(name, G, s):
        for label, lo, hi in (('at or under 1200', 0, 1200), ('above 1200', 1201, 99999)):
            V = [g for g in G if g['last'] >= 499 and lo <= g['cells'] <= hi]
            if not V:
                continue
            lens = [0] * 20
            for g in V:
                for f in g['feeds']:
                    if f[1] == s and f[8]:
                        lens[min(f[0] // 25, 19)] += f[2]
            fs = []
            for g in V:
                fr = sorted(f[0] for f in g['feeds'] if f[1] == s and f[8] and f[0] >= 150)
                fs.append(fr[4] if len(fr) >= 5 else 999)
            fs.sort()
            n = len(V)
            print('%s, %s, %d full games: died by choice r200-299 %.0f, r300-399 %.0f, r400-499 %.0f | per 25 rounds from r300: %s | longest r300/400/499 %.1f/%.1f/%.1f, second r400/499 %.1f/%.1f, alive %.0f/%.0f/%.0f, total %.0f/%.0f/%.0f | fifth death by choice after r150, median r%d' % (
                name, label, n, sum(lens[8:12]) / n, sum(lens[12:16]) / n, sum(lens[16:20]) / n, ' '.join('%.0f' % (b / n) for b in lens[12:]),
                mean(at(g, 300, s) for g in V), mean(at(g, 400, s) for g in V), mean(at(g, 499, s) for g in V),
                mean(at(g, 400, 2 + s) for g in V), mean(at(g, 499, 2 + s) for g in V),
                mean(at(g, 300, 4 + s) for g in V), mean(at(g, 400, 4 + s) for g in V), mean(at(g, 499, 4 + s) for g in V),
                mean(at(g, 300, 6 + s) for g in V), mean(at(g, 400, 6 + s) for g in V), mean(at(g, 499, 6 + s) for g in V), fs[len(fs) // 2]))
    hist('rank-1', load(('T0', 'T1')), 0)
    allg = load(ON)
    for opp in ('WeHaveQuizzes', 'Big Bobs Bots'):
        hist(opp, [g for g in allg if g['opp'] == opp], 1)
    for arm, tags in ARMS:
        hist('ours ' + arm, load(tags), 0)
    hist('ours ladder', load(('L0', 'L1')), 0)


def rams():
    for name, tags in (('online, three arms', ON), ('ladder', ('L0', 'L1'))):
        G = load(tags)
        alld = [(g, d) for g in G for d in g['tdeaths'] if d['s'] == 0 and d['L'] >= 8]
        R0 = [(g, d) for g, d in alld if d.get('ram') and d['reason'] == 3 and d['ram']['s'] == 1]
        print('%s: %d games; deaths of our longest at 8+: %d, rammed %d; rammer length median %s (2 to 5: %d), steps median %s, from median %s tiles, paid %d; none of ours within 5: %d; after r400: %d; our length median %s, round median %s' % (
            name, len(G), len(alld), len(R0), median(d['ram']['L'] for g, d in R0), sum(1 for g, d in R0 if d['ram']['L'] <= 5), median(d['ram']['steps'] for g, d in R0),
            median(d['ram']['mdist'] for g, d in R0), sum(1 for g, d in R0 if d['ram']['steps'] > d['ram']['free']), sum(1 for g, d in R0 if d['own5'] == 0),
            sum(1 for g, d in R0 if d['r'] >= 400), median(d['L'] for g, d in R0), median(d['r'] for g, d in R0)))
        for lo in (8, 12, 16, 20, 31):
            R = [(g, d) for g, d in R0 if d['L'] >= lo]
            H = [(g, d) for g, d in R if d['last'] and d['last']['r'] >= d['r'] - 1 and d['last'].get('clean') is not None]
            P = [(g, d) for g, d in H if d['prev'] and d['prev'].get('clean') is not None]
            D = [(g, d) for g, d in R if not g['win'] and in_race(g) and d['L'] > g['final'][1]]
            DH = [(g, d) for g, d in D if d['last'] and d['last']['r'] >= d['r'] - 1 and d['last'].get('clean') is not None]

            def av(X, z):
                return sum(1 for g, d in X if d['last']['endthr'][z] and d['last']['clean'][z])
            print('  at least %d: rammed %d, with a last-turn record %d, rammer in view %d | a clean tile existed: card-54 ring %d (both last turns %d of %d), full ring in view %d, full ring all enemies %d | stood in the ring with a clean tile: %d, %d, %d | decisive rams %d in %d games, avoidable %d, %d, %d' % (
                lo, len(R), len(H), sum(1 for g, d in H if d['ram'].get('then') and d['ram']['then'][0] <= 3),
                sum(1 for g, d in H if d['last']['clean'][3]), sum(1 for g, d in P if d['prev']['clean'][3] and d['last']['clean'][3]), len(P),
                sum(1 for g, d in H if d['last']['clean'][2]), sum(1 for g, d in H if d['last']['clean'][0]),
                av(H, 3), av(H, 2), av(H, 0), len(D), len(set(g['game'] for g, d in D)), av(DH, 3), av(DH, 2), av(DH, 0)))


def two():
    for name, tags in (('online', ON), ('ladder', ('L0', 'L1'))):
        G = load(tags)
        race = [g for g in G if in_race(g) and g['decided'] != 'elimination']
        won = [g for g in race if g['win']]
        lost = [g for g in race if not g['win']]
        ahead = []
        for g in lost:
            ds = [d for d in g['tdeaths'] if d['s'] == 0 and d['L'] >= 8 and d['L'] > d['opp']]
            if ds:
                ahead.append((max(d['L'] for d in ds), g['final'][1]))
        theirs = 0
        ours_ram = 0
        for g in won:
            ds = [d for d in g['tdeaths'] if d['s'] == 1 and d['L'] >= 8 and d['L'] > g['final'][0]]
            if ds:
                theirs += 1
                d = max(ds, key=lambda d: d['L'])
                ours_ram += int(d['reason'] == 3 and not d['own'] and bool(d.get('ram')) and d['ram']['s'] == 0)
        print('%s: won on length %d, lost %d | wins a halved longest would lose %d | lost games where our longest (8+) died while ahead %d: its full length beats their final %d, half of it %d | wins in which their longest died while longer than our final %d (by our ram %d)' % (
            name, len(won), len(lost), sum(1 for g in won if g['final'][0] / 2 <= g['final'][1]), len(ahead), sum(1 for a in ahead if a[0] > a[1]),
            sum(1 for a in ahead if a[0] / 2 > a[1]), theirs, ours_ram))


def fate():
    for arm, tags in ARMS + (('rank-1', ('T0', 'T1')), ('ladder', ('L0', 'L1'))):
        G = load(tags)
        for label, lo, hi in (('at or under 1200', 0, 1200), ('above 1200', 1201, 99999)):
            V = [g for g in G if lo <= g['cells'] <= hi]
            row = []
            for bk in (2, 3, 4):
                ff = [sum(g['feedfate'][0][bk][c] for g in V) for c in range(5)]
                tot = max(sum(ff), 1)
                reach = [g for g in V if g['last'] >= bk * 100]
                ln = sum(g['deaths'][0][bk][9] for g in reach) / max(1, len(reach))
                row.append('r%d00: length %.0f, pearls to the longest %d%%, other 8+ %d%%, short %d%%, enemy %d%%, nobody %d%%' % (
                    bk, ln, 100 * ff[0] // tot, 100 * ff[1] // tot, 100 * ff[2] // tot, 100 * ff[3] // tot, 100 * ff[4] // tot))
            print(arm, label, len(V), ' | '.join(row))


def lost():
    G = load(ON)
    L = [g for g in G if in_race(g) and not g['win']]
    nw = [g for g in L if g['decided'] != 'elimination']
    gaps = [g['final'][1] - g['final'][0] for g in nw]

    def peak(g):
        return max(sn[0] for r, sn in enumerate(g['snaps']) if r >= 150)
    print('online games %d, won %d, race %d, lost race %d: wiped out %d, on length %d (above 1200 cells %d)' % (
        len(G), sum(g['win'] or 0 for g in G), sum(1 for g in G if in_race(g)), len(L), len(L) - len(nw), len(nw), sum(1 for g in nw if g['cells'] > 1200)))
    print('on length: never above their final %d; gap median %s, up to 6: %d, up to 10: %d, up to 12: %d, above 20: %d; our total at the end at least theirs %d, at least 0.8 of theirs %d' % (
        sum(1 for g in nw if peak(g) <= g['final'][1]), median(gaps), sum(1 for x in gaps if x <= 6), sum(1 for x in gaps if x <= 10), sum(1 for x in gaps if x <= 12),
        sum(1 for x in gaps if x > 20), sum(1 for g in nw if g['final'][6] >= g['final'][7]), sum(1 for g in nw if g['final'][6] >= 0.8 * g['final'][7])))


def main():
    what = sys.argv[1]
    if what == 'size':
        size()
    elif what == 'rams':
        rams()
    elif what == 'two':
        two()
    elif what == 'fate':
        fate()
    elif what == 'lost':
        lost()


main()

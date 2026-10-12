"""Scratch (diag-longest): tables from lg_scan-*.jsonl.
Usage: python3 lg_agg.py games | grow | deaths | cross   (online arms)      python3 lg_agg.py grow ladder|top1"""
import sys
import json
from pathlib import Path
from statistics import median, mean
from collections import Counter, defaultdict

WORK = Path('data/analysis/ladder/dossier/work')
ARMS = dict(MAIN=('m1', 'm2', 'm3'), B7=('b1', 'b2'), B7Q=('q1', 'q2'))
MARKS = (100, 150, 200, 250, 300, 350, 400, 450, 499)
CAUSE = ('wall', 'own body', 'body', 'rammed it', 'was rammed', 'unpaid', 'bad split', 'no action')
CATS = ('nat', 'feed', 'own', 'opp')


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


def both_queens_dead(g):
    return g['qdeath'][0] is not None and g['qdeath'][1] is not None


def in_race(g):
    return g['decided'] in ('longest', 'total') or (g['decided'] == 'elimination' and both_queens_dead(g))


def crossing(g):
    """Round from which the final leader on longest dragon is ahead for good, and what happened in that round."""
    sn = g['snaps']
    n = len(sn)
    lead = 1 if sn[-1][1] > sn[-1][0] else 0 if sn[-1][0] > sn[-1][1] else -1
    if lead < 0:
        return None
    X = 0
    for r in range(n - 1, -1, -1):
        if sn[r][1 - lead] >= sn[r][lead]:
            X = r + 1
            break
    if X >= n:
        return None
    lose = 1 - lead
    prev = sn[X - 1] if X > 0 else None
    what = '?'
    det = None
    if prev is None:
        what = 'from the start'
    elif sn[X][lose] < prev[lose]:
        ds = [d for d in g['tdeaths'] if d['s'] == lose and d['r'] == X and d['L'] >= prev[lose]]
        sp = [t for t in g['tsplits'] if t[1] == lose and t[0] == X and t[2] >= prev[lose]]
        if ds:
            d = ds[0]
            code = (0, 1, 2, 3 if d['own'] else 4, 5 + (d['act'] if d['act'] is not None else 2))[min(d['reason'], 4)]
            what = 'died:' + CAUSE[code]
            det = d
        elif sp:
            what = 'split %d>%d+%d' % (sp[0][2], sp[0][3], sp[0][4])
        else:
            ds2 = [d for d in g['tdeaths'] if d['s'] == lose and X - 1 <= d['r'] <= X]
            if ds2:
                d = ds2[-1]
                code = (0, 1, 2, 3 if d['own'] else 4, 5 + (d['act'] if d['act'] is not None else 2))[min(d['reason'], 4)]
                what = 'died:' + CAUSE[code]
                det = d
            else:
                what = 'shrank'
    else:
        eats = Counter(CATS[e[2]] for e in g['roundeat'] if e[0] == X and e[1] == lead)
        what = 'outgrown:' + '+'.join('%s%d' % kv for kv in sorted(eats.items())) if eats else 'outgrown'
    return dict(lead=lead, X=X, what=what, det=det, before=prev[:2] if prev else None, after=sn[X][:2])


def ramtxt(d):
    r = d.get('ram')
    if not r:
        return ''
    th = r.get('then')
    return ' by #%d L%d from %d tiles, %d steps (%d free), %s; own heads within 5: %d' % (
        r['id'], r['L'], r['mdist'], r['steps'], r['free'],
        'not near at its last turn' if th is None else 'in view' if th[0] <= 3 else 'out of view (cheb %d)' % th[0], d['own5'])


def games():
    lines = []
    for arm, tags in ARMS.items():
        G = load(tags)
        if not G:
            continue
        dec = Counter(g['decided'] for g in G)
        race = [g for g in G if in_race(g)]
        lines.append('## %s: %d games, won %d; decided queen %d, longest %d, total %d, elimination %d (both queens dead first: %d)' % (
            arm, len(G), sum(g['win'] or 0 for g in G), dec['queen'], dec['longest'], dec['total'], dec['elimination'],
            sum(1 for g in G if g['decided'] == 'elimination' and both_queens_dead(g))))
        lines.append('race games %d, won %d' % (len(race), sum(g['win'] or 0 for g in race)))
        lines.append('game | map | opp | cells | res | by | ours/theirs longest at ' + ' '.join(str(m) for m in MARKS) + ' | X | what')
        for g in sorted(race, key=lambda g: (g['opp'], g['game'])):
            c = crossing(g)
            row = ' '.join('%d/%d' % (at(g, m, 0), at(g, m, 1)) for m in MARKS)
            what = ''
            if c:
                what = 'r%d %s %s (%d/%d > %d/%d)' % (c['X'], 'they pass' if c['lead'] == 1 else 'we pass', c['what'],
                                                     c['before'][0] if c['before'] else 0, c['before'][1] if c['before'] else 0, c['after'][0], c['after'][1])
                if c['det']:
                    what += ' L%d%s' % (c['det']['L'], ramtxt(c['det']))
            lines.append('%d | %s | %s | %d | %s | %s%s | %s | %s' % (g['game'], g['map'], g['opp'][:3], g['cells'], 'W' if g['win'] else 'L', g['decided'][:4],
                                                                 '' if g['last'] >= 499 else ' r%d' % g['last'], row, what))
        lines.append('')
    print('\n'.join(lines))


def cross():
    for arm, tags in ARMS.items():
        G = load(tags)
        race = [g for g in G if in_race(g)]
        if not race:
            continue
        cl = Counter()
        xs = defaultdict(list)
        for g in race:
            c = crossing(g)
            res = 'W' if g['win'] else 'L'
            if c is None:
                cl[res, 'level'] += 1
                continue
            w = c['what'].split(':')[0] if c['what'].startswith('outgrown') else c['what'].split(' ')[0] if c['what'].startswith('split') else c['what']
            cl[res, w] += 1
            xs[res].append(c['X'])
        print(arm, 'race', len(race))
        for k, v in sorted(cl.items()):
            print('   ', k, v)
        for res in 'WL':
            if xs[res]:
                v = sorted(xs[res])
                print('   X', res, 'n', len(v), 'median', median(v), 'before r200', sum(1 for x in v if x < 200), 'r200-399', sum(1 for x in v if 200 <= x < 400), 'r400+', sum(1 for x in v if x >= 400))


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


def grow(mode):
    for name, G, s in groups(mode):
        n = len(G)
        print('== %s: %d games' % (name, n))
        print('  longest at', ' '.join('r%d: %.1f (med %d)' % (m, mean(at(g, m, s) for g in G), median(at(g, m, s) for g in G)) for m in MARKS))
        print('  second  at', ' '.join('r%d: %.1f' % (m, mean(at(g, m, 2 + s) for g in G)) for m in MARKS))
        print('  alive   at', ' '.join('r%d: %.1f' % (m, mean(at(g, m, 4 + s) for g in G)) for m in MARKS))
        for bk in range(5):
            reach = [g for g in G if g['last'] >= bk * 100]
            k = len(reach)
            if not k:
                continue
            le = [sum(1 for e in g['roundeat'] if e[1] == s and e[0] // 100 == bk and e[4] >= 8 and e[2] == c) for c in range(4) for g in reach]
            lec = [sum(le[c * k:(c + 1) * k]) / k for c in range(4)]
            ae = [sum(g['alleat'][s][bk][c] for g in reach) / k for c in range(4)]
            dl = sum(g['deaths'][s][bk][9] for g in reach) / k
            dp = sum(g['deaths'][s][bk][10] for g in reach) / k
            nd = sum(1 for g in reach for f in g['feeds'] if f[1] == s and f[0] // 100 == bk and f[8]) / k
            ndnear = sum(1 for g in reach for f in g['feeds'] if f[1] == s and f[0] // 100 == bk and f[8] and f[3] <= 3 and f[4] >= 8) / k
            boxed = sum(g['deaths'][s][bk][11] for g in reach) / k
            ff = [sum(g['feedfate'][s][bk][c] for g in reach) / k for c in range(5)]
            gain = mean(at(g, min(bk * 100 + 99, 499), s) - at(g, bk * 100, s) for g in reach)
            tsp = sum(1 for g in reach for t in g['tsplits'] if t[1] == s and t[0] // 100 == bk and t[2] >= 8) / k
            tde = sum(1 for g in reach for d in g['tdeaths'] if d['s'] == s and d['r'] // 100 == bk and d['L'] >= 8) / k
            tdl = sum(d['L'] for g in reach for d in g['tdeaths'] if d['s'] == s and d['r'] // 100 == bk and d['L'] >= 8) / k
            dall = sum(g['deaths'][s][bk][8] for g in reach) / k
            print('  r%d-%d (%d games): longest %+.1f | top(8+) eats nat %.1f feed %.1f own-dead %.1f their-dead %.1f | all eats %.0f/%.0f/%.0f/%.0f | by-choice deaths %.1f (len %.1f, pearls %.1f; beside a top of 8+: %.1f) boxed %.1f | their pearls to: top %.1f, other 8+ %.1f, short %.1f, enemy %.1f, none %.1f | top(8+) splits %.2f deaths %.2f (len %.1f) | all death len %.0f' % (
                bk * 100, bk * 100 + 99, k, gain, lec[0], lec[1], lec[2], lec[3], ae[0], ae[1], ae[2], ae[3], nd, dl, dp, ndnear, boxed,
                ff[0], ff[1], ff[2], ff[3], ff[4], tsp, tde, tdl, dall))
        lt = [[sum(g['lt'][s][b][z] for g in G) for z in range(14)] for b in range(5)]
        for b, lo in enumerate((8, 12, 16, 20, 31)):
            r = lt[b]
            if r[0]:
                print('  top turns L%d+: %d, enemy within 12: %d, ended inside a true ring %d (clean tile was there %d), inside a ring in view %d (clean %d), no clean tile %d (in view %d), multi-step %d, rammed before next turn %d (%.2f per 100)' % (
                    lo, r[0], r[1], r[2], r[3], r[6], r[7], r[10], r[11], r[12], r[13], 100.0 * r[13] / r[0]))


def deaths(mode):
    for name, G, s in groups(mode):
        D = [(g, d) for g in G for d in g['tdeaths'] if d['s'] == s]
        print('== %s: %d games, top deaths (6+) %d' % (name, len(G), len(D)))
        for lo in (8, 12, 16, 20, 31):
            sel = [(g, d) for g, d in D if d['L'] >= lo]
            if not sel:
                continue
            cz = Counter()
            for g, d in sel:
                code = (0, 1, 2, 3 if d['own'] else 4, 5 + (d['act'] if d['act'] is not None else 2))[min(d['reason'], 4)]
                cz[CAUSE[code]] += 1
            rams = [(g, d) for g, d in sel if d.get('ram') and d['reason'] == 3 and d['ram']['s'] != s]
            print('  L%d+: %d deaths in %d games; %s' % (lo, len(sel), len(set(g['game'] for g, d in sel)), dict(cz)))
            if not rams:
                continue
            rl = sorted(d['ram']['L'] for g, d in rams)
            stp = sorted(d['ram']['steps'] for g, d in rams)
            md = sorted(d['ram']['mdist'] for g, d in rams)
            paid = sum(1 for g, d in rams if d['ram']['steps'] > d['ram']['free'])
            have = [(g, d) for g, d in rams if d['last'] and d['last']['r'] >= d['r'] - 1 and d['last'].get('clean') is not None]
            inview = sum(1 for g, d in have if d['ram'].get('then') and d['ram']['then'][0] <= 3)
            c_true = sum(1 for g, d in have if d['last']['clean'][0])
            c_54 = sum(1 for g, d in have if d['last']['clean'][1])
            c_tv = sum(1 for g, d in have if d['last']['clean'][2])
            e_true = sum(1 for g, d in have if d['last']['endthr'][0])
            e_54 = sum(1 for g, d in have if d['last']['endthr'][1])
            e_54v = sum(1 for g, d in have if d['last']['endthr'][3])
            avoid_true = sum(1 for g, d in have if d['last']['endthr'][0] and d['last']['clean'][0])
            avoid_54 = sum(1 for g, d in have if d['last']['endthr'][1] and d['last']['clean'][1])
            avoid_54v = sum(1 for g, d in have if d['last']['endthr'][3] and d['last']['clean'][3])
            avoid_tv = sum(1 for g, d in have if d['last']['endthr'][2] and d['last']['clean'][2])
            hp = [(g, d) for g, d in have if d['prev'] and d['prev'].get('clean') is not None]
            p_clean = sum(1 for g, d in hp if d['prev']['clean'][0])
            p_both = sum(1 for g, d in hp if d['prev']['clean'][0] and d['last']['clean'][0])
            multi = sum(1 for g, d in have if d['last']['steps'] > 1)
            alone = sum(1 for g, d in rams if d['own5'] == 0)
            dec = sum(1 for g, d in rams if not g['win'] and d['L'] > g['final'][1 - s] and in_race(g))
            print('     rammed %d (in %d games, lost %d): rammer L median %d (2-5: %d), steps median %d, from median %d tiles (1-3: %d), paid for the lunge %d; none of its own within 5: %d; R at end %s' % (
                len(rams), len(set(g['game'] for g, d in rams)), len(set(g['game'] for g, d in rams if not g['win'])), rl[len(rl) // 2], sum(1 for x in rl if x <= 5), stp[len(stp) // 2], md[len(md) // 2],
                sum(1 for x in md if x <= 3), paid, alone, ''))
            print('     with a last-turn record %d: rammer in view then %d; ended inside a true ring %d, a free+1 ring %d (in view %d); a clean tile existed: true %d, free+1 %d, true in view %d; ended in ring AND clean tile existed: true %d, free+1 %d, true-in-view %d, free+1-in-view %d; last move multi-step %d; turn before: clean %d of %d, both turns %d; longer than their final longest in a lost race game %d' % (
                len(have), inview, e_true, e_54, e_54v, c_true, c_54, c_tv, avoid_true, avoid_54, avoid_tv, avoid_54v, multi, p_clean, len(hp), p_both, dec))


def main():
    what = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'online'
    if what == 'games':
        games()
    elif what == 'cross':
        cross()
    elif what == 'grow':
        grow(mode)
    elif what == 'deaths':
        deaths(mode)


main()

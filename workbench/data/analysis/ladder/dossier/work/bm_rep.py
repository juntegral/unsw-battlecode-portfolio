"""Scratch (diag-bigmap): the cells of the report's tables 2 to 4 in compact form, from the scan rows.
Usage: python3 data/analysis/ladder/dossier/work/bm_rep.py"""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from collections import Counter, defaultdict
from statistics import median, mean

WORK = Path('data/analysis/ladder/dossier/work')
BANDS = ((0, 100), (101, 200), (201, 300), (301, 400), (401, 500))


def load():
    rows = []
    for p in sorted(WORK.glob('bm_scan-O[0-9].jsonl')):
        for line in p.read_text().splitlines():
            g = json.loads(line)
            if g['cells'] > 1200:
                rows.append(g)
    rows.sort(key=lambda g: g['gid'])
    return rows


def band(r):
    for k, (a, b) in enumerate(BANDS):
        if a <= r <= b:
            return k
    return 4


def klass(d):
    c = d['c']
    if c == 'head-on':
        if not d['cross']:
            return 'crash'
        return 'rammed' if d['role'] == 'hit' else 'rammer'
    if c == 'no action' and d.get('fed'):
        return 'fed'
    return 'crash'


def at(g, r):
    return g['snap'][min(r, g['last'])]


def f5(v, n):
    return ' / '.join('%.0f' % (x / n) for x in v) + ' = %.0f' % (sum(v) / n)


def account(name, gs):
    n = len(gs)
    print()
    print('=====', name, n, 'games, won', sum(g['result'] == 'win' for g in gs))
    for s, nm in ((0, 'ours'), (1, 'theirs')):
        ln = defaultdict(lambda: [0] * 5)
        cn = defaultdict(lambda: [0] * 5)
        for g in gs:
            for d in g['deaths']:
                if d['s'] == s:
                    ln[klass(d)][band(d['r'])] += d['L']
                    cn[klass(d)][band(d['r'])] += 1
        eat = [[0] * 5, [0] * 5]
        paid = [0] * 5
        for g in gs:
            for row in g['rc']:
                b = band(row[0])
                eat[0][b] += row[1 + s * 6 + 2]
                eat[1][b] += row[1 + s * 6 + 3]
                paid[b] += row[1 + s * 6 + 5]
        for k in ('rammed', 'rammer', 'crash', 'fed'):
            print('  %s %-7s length %s | deaths %s' % (nm, k, f5(ln[k], n), f5(cn[k], n)))
        print('  %s paid    %s' % (nm, f5(paid, n)))
        print('  %s natural %s' % (nm, f5(eat[0], n)))
        print('  %s drops   %s' % (nm, f5(eat[1], n)))
        net = [eat[0][b] + eat[1][b] - paid[b] - sum(ln[k][b] for k in ln) for b in range(5)]
        print('  %s net     %s' % (nm, f5(net, n)))
        # crash split
        cr = Counter()
        for g in gs:
            for d in g['deaths']:
                if d['s'] == s and klass(d) == 'crash':
                    c = d['c']
                    key = 'wall' if c == 'wall' else 'own body' if c == 'own body' else 'mate body' if c == 'other body' and d.get('hit') == 'mate' else 'enemy body' if c == 'other body' else 'no order, boxed' if c == 'no action' and d.get('free') == 0 else 'mate head-on' if c == 'head-on' else 'other'
                    cr[key] += d['L']
        print('  %s crash length a game by kind: %s' % (nm, '; '.join('%s %.0f' % (k, v / n) for k, v in cr.most_common())))
    for s, nm in ((0, 'rams on us'), (1, 'rams on them')):
        v = [d for g in gs for d in g['deaths'] if d['s'] == s and d['c'] == 'head-on' and d['cross'] and d['role'] == 'hit']
        m = len(v)
        c = Counter(min(d['m']['L0'], 5) for d in v)
        st = Counter(min(d['m']['steps'], 4) for d in v)
        vl = Counter(2 if d['L'] == 2 else 3 if d['L'] == 3 else 4 if d['L'] == 4 else 5 if d['L'] < 10 else 10 for d in v)
        rel = Counter('shorter' if d['L'] < d['m']['L0'] else 'same' if d['L'] == d['m']['L0'] else 'longer' if d['L'] < 2 * d['m']['L0'] else 'twice' for d in v)
        z = Counter(('own' if zz < 0.35 else 'their' if zz > 0.65 else 'mid') for zz in ((d['zo'] if s == 0 else 1 - d['zo']) for d in v))
        dv = sum(d['drop'] for d in v)
        mv = [d for g in gs for d in g['deaths'] if d['s'] == 1 - s and d['c'] == 'head-on' and d['cross'] and d['role'] == 'mover']
        dm = sum(d['drop'] for d in mv)
        over = sum(1 for d in v if d['m']['steps'] > (d['m']['L0'] + 3) // 4 + d['m']['L0'] - 2)
        print('  %s: %.1f a game; rammer 2/3/4/5+ %s; steps 1/2/3/4+ %s, mean %.2f; paid %.2f a ram, any %.2f; a pearl eaten on the way %.2f, beyond its reach without one %.2f; victim 2/3/4/5-9/10+ %s, mean %.2f; victim shorter/same/longer/twice %s; rammer has the head count %.2f; victim alone within 5 %.2f, enemy heads within 5 %.2f; victim-side third own/mid/their %s' % (
            nm, m / n, ' '.join('%.2f' % (c[k] / m) for k in (2, 3, 4, 5)), ' '.join('%.2f' % (st[k] / m) for k in (1, 2, 3, 4)), mean(d['m']['steps'] for d in v), mean(d['m']['paid'] for d in v), sum(d['m']['paid'] > 0 for d in v) / m,
            sum(d['m']['ate'] > 0 for d in v) / m, over / m, ' '.join('%.2f' % (vl[k] / m) for k in (2, 3, 4, 5, 10)), mean(d['L'] for d in v), ' '.join('%.2f' % (rel[k] / m) for k in ('shorter', 'same', 'longer', 'twice')),
            sum(d['m']['edge'] >= 1 for d in v) / m, sum(d['o5'] == 0 for d in v) / m, mean(d['e5'] for d in v), ' '.join('%.2f' % (z[k] / m) for k in ('own', 'mid', 'their'))))
        print('     drops of the victim: victim side eats %.2f, rammer side %.2f; drops of the rammer: victim side %.2f, rammer side %.2f; length lost a ram: victim %.2f, rammer %.2f' % (
            sum(d['eat'][s] for d in v) / dv, sum(d['eat'][1 - s] for d in v) / dv, sum(d['eat'][s] for d in mv) / dm, sum(d['eat'][1 - s] for d in mv) / dm, mean(d['L'] for d in v), mean(d['m']['L'] for d in v)))
        pv = sum(d['eat'][s] for d in v) + sum(d['eat'][s] for d in mv)
        pr = sum(d['eat'][1 - s] for d in v) + sum(d['eat'][1 - s] for d in mv)
        paidr = sum(d['m']['paid'] for d in v)
        print('     net a ram after the drops: victim side %.2f, rammer side %.2f; a game: victim side %.0f, rammer side %.0f' % (
            (pv - sum(d['L'] for d in v)) / m, (pr - sum(d['m']['L'] for d in v) - paidr) / m, (pv - sum(d['L'] for d in v)) / n, (pr - sum(d['m']['L'] for d in v) - paidr) / n))


def habits(name, gs):
    n = len(gs)
    print()
    print('=====', name, n, 'games')
    for s, nm in ((0, 'ours'), (1, 'theirs')):
        o = s * 4
        print('  %s count r150/200/300/400/end median: %s; total: %s; longest: %s; queen alive of %d: %s; queen length alive median: %s' % (
            nm, ' '.join('%g' % median(at(g, r)[o] for g in gs) for r in (150, 200, 300, 400, 499)), ' '.join('%g' % median(at(g, r)[o + 1] for g in gs) for r in (150, 200, 300, 400, 499)),
            ' '.join('%g' % median(at(g, r)[o + 2] for g in gs) for r in (150, 200, 300, 400, 499)), n, ' '.join('%d' % sum(at(g, r)[o + 3] > 0 for g in gs) for r in (100, 150, 200, 300, 400, 499)),
            ' '.join('%g' % (median([at(g, r)[o + 3] for g in gs if at(g, r)[o + 3] > 0] or [0])) for r in (150, 200, 300, 400, 499))))
        for L in (10, 20):
            fr = []
            for g in gs:
                r = g['last']
                while r >= 0 and g['snap'][r][o + 2] >= L:
                    r -= 1
                fr.append(r + 1 if r + 1 <= g['last'] else 999)
            print('  %s longest %d+ for good from round (median) %g; never %d' % (nm, L, median(fr), sum(1 for x in fr if x == 999)))
        mix = [0] * 6
        for g in gs:
            for row in g['hist']:
                if row[0] == 300:
                    for k in range(6):
                        mix[k] += row[1 + s][k]
        print('  %s length mix at r300 a game (2/3/4/5-7/8-14/15+): %s' % (nm, ' '.join('%.1f' % (x / n) for x in mix)))
        sp = Counter()
        for g in gs:
            for b, sd, L, child, cnt in g['splits']:
                if sd == s and 3 <= b <= 7:
                    sp['4' if L == 4 else '5-7' if L <= 7 else '8+'] += cnt
        print('  %s splits r150-399 a game by length before: %s' % (nm, ' '.join('%s: %.0f' % (k, sp[k] / n) for k in ('4', '5-7', '8+'))))
        fd = [0] * 5
        fl = [0] * 5
        for g in gs:
            for d in g['deaths']:
                if d['s'] == s and d.get('fed'):
                    fd[band(d['r'])] += 1
                    fl[band(d['r'])] += d['L']
        print('  %s feeders a game by band %s; length %s; mean feeder length %.2f' % (nm, f5(fd, n), f5(fl, n), sum(fl) / max(sum(fd), 1)))
        e = Counter()
        for g in gs:
            for b, sd, kind, top, origin, cnt in g['eats']:
                if sd == s and b >= 6:
                    cls = 'queen' if kind == 'q' else '10+' if kind == 10 else 'rest'
                    e[(cls, origin)] += cnt
        for cls in ('queen', '10+'):
            tot = sum(e[(cls, og)] for og in range(4))
            print('  %s pearls eaten from r300 a game by %s: %.1f; natural %.2f, own feeders %.2f, own other dead %.2f, enemy dead %.2f' % (nm, cls, tot / n, e[(cls, 0)] / max(tot, 1), e[(cls, 1)] / max(tot, 1), e[(cls, 2)] / max(tot, 1), e[(cls, 3)] / max(tot, 1)))
        pos = Counter()
        m = 0
        for g in gs:
            for row in g['pos']:
                if row[0] in (100, 200, 300, 400):
                    m += 1
                    for k in range(6):
                        pos[k] += row[1 + s][k]
        print('  %s short heads (2-4) at r100-400 a sample: own third %.1f, middle %.1f, other third %.1f; 5+: %.1f %.1f %.1f' % (nm, pos[0] / m, pos[1] / m, pos[2] / m, pos[3] / m, pos[4] / m, pos[5] / m))
        qd = [d for g in gs for d in g['deaths'] if d['s'] == s and d['q']]
        c = Counter('rammed' if (d['c'] == 'head-on' and d.get('role') == 'hit') else 'rammer' if d['c'] == 'head-on' else d['c'] for d in qd)
        print('  %s queen deaths %d of %d: %s; median round %g; at length 2/3/4+ %d/%d/%d' % (nm, len(qd), n, dict(c), median([d['r'] for d in qd] or [0]), sum(d['L'] == 2 for d in qd), sum(d['L'] == 3 for d in qd), sum(d['L'] >= 4 for d in qd)))


rows = load()
sets = (('MAIN', [g for g in rows if g['arm'] == 'MAIN']), ('NEW (B7 and B7Q)', [g for g in rows if g['arm'] != 'MAIN']))
for name, gs in sets:
    account(name, gs)
for name, gs in sets:
    habits(name, gs)
for opp in ('Big Bobs Bots', 'WeHaveQuizzes'):
    habits('NEW vs ' + opp, [g for g in rows if g['arm'] != 'MAIN' and g['opp'] == opp])

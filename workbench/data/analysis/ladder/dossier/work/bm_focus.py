"""Scratch (diag-bigmap): focused counts for the report: what a short dragon does next to a long enemy head, the
feeding clock of each game, rams on long dragons, whether crash deaths had a free tile.
Usage: python3 data/analysis/ladder/dossier/work/bm_focus.py [O|L|R] [min cells] [part]"""
import sys, json
sys.dont_write_bytecode = True
from pathlib import Path
from collections import Counter, defaultdict
from statistics import median, mean

WORK = Path('data/analysis/ladder/dossier/work')


def load(src, lo):
    rows = []
    for p in sorted(WORK.glob('bm_scan-' + src + '[0-9].jsonl')):
        for line in p.read_text().splitlines():
            g = json.loads(line)
            if g['cells'] > lo:
                rows.append(g)
    rows.sort(key=lambda g: (g['arm'], g['opp'], g['gid']))
    return rows


def at(g, r):
    return g['snap'][min(r, g['last'])]


def decider(g):
    f = g['final']
    if f[0] == 0 or f[4] == 0:
        return 'elim'
    if f[3] != f[7]:
        return 'queen'
    if f[2] != f[6]:
        return 'longest'
    return 'total'


def contact(name, gs):
    n = len(gs)
    print()
    print('== contact,', name, n, 'games: short non-queen turns that begin with an enemy head within 3 tiles; a game / share that ram / share rammed before the next turn')
    for s, nm in ((0, 'ours'), (1, 'theirs')):
        ct = defaultdict(lambda: [0, 0, 0])
        for g in gs:
            for b, sd, L0, Lt, g0, edge, oc, q, cnt, hit in g['contact']:
                if sd == s and not q and L0 <= 4:
                    tk = '10+' if Lt == 10 else '5-9' if Lt == 5 else 'same' if Lt == L0 else 'shorter' if Lt < L0 else 'longer 2-4'
                    for key in ((tk, L0, g0), (tk, 0, g0), (tk, 0, 0), (tk, L0, 0)):
                        ct[key][0] += cnt
                        ct[key][1] += cnt if oc == 'R' else 0
                        ct[key][2] += hit
        for tk in ('10+', '5-9', 'longer 2-4', 'same', 'shorter'):
            cells = []
            for L0 in (0, 2, 3, 4):
                for g0 in (0, 1, 2, 3):
                    x = ct[(tk, L0, g0)]
                    if x[0]:
                        cells.append('L%s d%s %.1f/%.3f/%.3f' % (L0 or 'all', g0 or 'all', x[0] / n, x[1] / x[0], x[2] / x[0]))
            print('  %s target %-10s %s' % (nm, tk, ' | '.join(cells)))


def clock(name, gs):
    print()
    print('== feeding clock,', name)
    out = []
    for g in gs:
        cnt = [x[0] for x in g['snap']]
        S = next((r for r in range(200, min(400, g['last']) + 1) if cnt[r] >= 56), 401)
        on = sum(1 for r in range(201, min(400, g['last']) + 1) if cnt[r] >= 56)
        fed = [d['r'] for d in g['deaths'] if d['s'] == 0 and d.get('fed')]
        resets = [(d['r'], d['L']) for d in g['deaths'] if d['s'] == 0 and d['L'] >= 10 and d['top'] and d['c'] == 'head-on' and d['cross'] and d['role'] == 'hit']
        longram = [(d['r'], d['L']) for d in g['deaths'] if d['s'] == 0 and d['L'] >= 10 and d['c'] == 'head-on' and d['cross'] and d['role'] == 'hit']
        f = g['final']
        row = dict(g=g, S=S, on=on, fed=len(fed), fed1=min(fed) if fed else None, resets=resets, longram=longram)
        out.append(row)
        print('  %d %-4s %-3s %-10s %-4s %-7s count r200/300/400 %d/%d/%d; S r%d; rounds fed-on in 201-400: %d; feeders %d (first r%s); ours longest r300/400/end %d/%d/%d; theirs longest end %d queen %d (ours %d); top 10+ rammed %s; any 10+ rammed %d' % (
            g['gid'], g['arm'], g['opp'][:3], g['map'][:10], g['result'], decider(g), at(g, 200)[0], at(g, 300)[0], at(g, 400)[0], S, on, len(fed), min(fed) if fed else '-',
            at(g, 300)[2], at(g, 400)[2], f[2], f[6], f[7], f[3], resets, len(longram)))
    for nm, test in (('S by r210', lambda r: r['S'] <= 210), ('S r211-400', lambda r: 210 < r['S'] <= 400), ('never 56 before r401', lambda r: r['S'] > 400)):
        v = [r for r in out if test(r)]
        if v:
            print('  %s: %d games, won %d; ours longest r300 median %g, r400 %g, end %g; theirs end %g; decided queen %d longest %d; lost on longest %d' % (
                nm, len(v), sum(r['g']['result'] == 'win' for r in v), median(at(r['g'], 300)[2] for r in v), median(at(r['g'], 400)[2] for r in v), median(r['g']['final'][2] for r in v),
                median(r['g']['final'][6] for r in v), sum(decider(r['g']) == 'queen' for r in v), sum(decider(r['g']) == 'longest' for r in v), sum(decider(r['g']) == 'longest' and r['g']['result'] == 'loss' for r in v)))


def longrams(name, gs):
    n = len(gs)
    print()
    print('== rams on dragons of 10 or more,', name, n, 'games')
    for s, nm in ((0, 'ours hit'), (1, 'theirs hit')):
        v = [d for g in gs for d in g['deaths'] if d['s'] == s and d['L'] >= 10 and d['c'] == 'head-on' and d['cross'] and d['role'] == 'hit']
        if not v:
            continue
        m = len(v)
        bands = ((0, 149), (150, 199), (200, 299), (300, 399), (400, 499))
        print('  %s: %d (%.2f a game), length %.1f a game; the longest of its side %d; by band %s: %s' % (nm, m, m / n, sum(d['L'] for d in v) / n, sum(d['top'] for d in v), bands, ' '.join('%d' % sum(1 for d in v if a <= d['r'] <= b) for a, b in bands)))
        print('     rammer length %s; steps %s; straight distance at its turn start %s; paid %s' % (sorted(Counter(min(d['m']['L0'], 7) for d in v).items()), sorted(Counter(min(d['m']['steps'], 6) for d in v).items()), sorted(Counter(min(d['m']['d0'], 7) for d in v).items()), sorted(Counter(min(d['m']['paid'], 3) for d in v).items())))
        print('     own heads within 5 of the victim: none %.2f, one %.2f, more %.2f; enemy heads within 5: one %.2f, two %.2f, more %.2f; victim length 10-14 %d, 15-29 %d, 30+ %d' % (
            sum(d['o5'] == 0 for d in v) / m, sum(d['o5'] == 1 for d in v) / m, sum(d['o5'] >= 2 for d in v) / m, sum(d['e5'] == 1 for d in v) / m, sum(d['e5'] == 2 for d in v) / m, sum(d['e5'] >= 3 for d in v) / m,
            sum(d['L'] <= 14 for d in v), sum(15 <= d['L'] <= 29 for d in v), sum(d['L'] >= 30 for d in v)))
        dv = sum(d['drop'] for d in v)
        print('     drops %d: eaten by victim side %.2f, rammer side %.2f; by a 10+ or longest of the rammer side %.2f' % (dv, sum(d['eat'][s] for d in v) / dv, sum(d['eat'][1 - s] for d in v) / dv, sum(d['eatB'][1 - s] for d in v) / dv))


def crashes(name, gs):
    n = len(gs)
    print()
    print('== crash deaths with a free tile,', name, n, 'games (a game: all / with at least one free side)')
    for s, nm in ((0, 'ours'), (1, 'theirs')):
        for c in ('wall', 'own body', 'other body', 'no action'):
            v = [d for g in gs for d in g['deaths'] if d['s'] == s and d['c'] == c and not d.get('fed')]
            if v:
                fr = [d for d in v if d.get('free', 0) > 0]
                print('  %s %-10s %.1f / %.1f (%.2f); length %.1f / %.1f; mean length %.2f / %.2f' % (nm, c, len(v) / n, len(fr) / n, len(fr) / len(v), sum(d['L'] for d in v) / n, sum(d['L'] for d in fr) / n, mean(d['L'] for d in v), mean(d['L'] for d in fr) if fr else 0))


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'O'
    lo = int(sys.argv[2]) if len(sys.argv) > 2 else 1200
    part = sys.argv[3] if len(sys.argv) > 3 else 'all'
    rows = load(src, lo)
    sets = [('ALL', rows)]
    if src == 'O':
        sets = [('MAIN', [g for g in rows if g['arm'] == 'MAIN']), ('B7+B7Q', [g for g in rows if g['arm'] != 'MAIN'])]
        for opp in sorted(set(g['opp'] for g in rows)):
            sets.append(('B7+B7Q vs ' + opp, [g for g in rows if g['arm'] != 'MAIN' and g['opp'] == opp]))
    for name, gs in sets:
        if part in ('all', 'contact'):
            contact(name, gs)
        if part in ('all', 'clock') and src == 'O' and name in ('MAIN', 'B7+B7Q'):
            clock(name, gs)
        if part in ('all', 'long'):
            longrams(name, gs)
        if part in ('all', 'crash'):
            crashes(name, gs)


if __name__ == '__main__':
    main()

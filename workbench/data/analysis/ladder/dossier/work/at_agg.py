"""Scratch (diag-attack): tables from at_scan-*.jsonl. Usage: python3 data/analysis/ladder/dossier/work/at_agg.py <section>
sections: ho (job 1), ch (job 2 overview), rule (our code rule against the chances), all"""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path

D = Path('data/analysis/ladder/dossier/work')
G = []
for n in range(5):
    with open(D / ('at_scan-%d.jsonl' % n)) as f:
        for line in f:
            G.append(json.loads(line))
NG = len(G)
for g in G:
    g['grow'] = 150 if g['cells'] > 1200 else 300
    s300 = g['series'].get('300')
    g['feed'] = 300 if (g['cells'] > 600 and s300 and s300[3] > 0) else 400
    g['aggr'] = g['cells'] <= 1200


def phase(g, r, n_ours):
    if r > g['feed']:
        return 'C'
    if r > 200 and n_ours >= 56:
        return 'F'
    return 'A' if r <= g['grow'] else 'B'


def lc(L):
    return '2' if L <= 2 else '3' if L == 3 else '4' if L == 4 else '5-7' if L <= 7 else '8-14' if L <= 14 else '15+'


def tc(L):
    return '2' if L <= 2 else '3' if L == 3 else '4' if L == 4 else '5-9' if L <= 9 else '10-19' if L <= 19 else '20+'


def pct(a, b):
    return '%.3f' % (a / b) if b else 'NA'


def dist_line(c, order):
    n = sum(c.values())
    return ' '.join('%s:%.3f' % (k, c[k] / n) for k in order if n) + ' (n=%d)' % n


def ho_tables():
    print('== job 1: cross-team head-on meetings, %d games ==' % NG)
    for ms, name in ((1, 'THEY ram us'), (0, 'WE ram them')):
        H = [(g, x) for g in G for x in g['hos'] if x['cross'] and x['ms'] == ms]
        print()
        print('%s: %d meetings, %.1f a game' % (name, len(H), len(H) / NG))
        for lab, lo, hi in (('r0-100', 0, 100), ('r101-300', 101, 300), ('r301-500', 301, 500), ('all', 0, 500)):
            S = [(g, x) for g, x in H if lo <= x['r'] <= hi]
            if not S:
                continue
            n = len(S)
            a = Counter()
            cm, cv, cd, cp, ce = Counter(), Counter(), Counter(), Counter(), Counter()
            for g, x in S:
                cm[lc(x['L0'])] += 1
                cv[tc(x['Lv'])] += 1
                cd[str(min(x['k'], 4)) if x['k'] < 4 else '4+'] += 1
                cp[str(min(x['paid'], 3)) if x['paid'] < 3 else '3+'] += 1
                ce['more' if x['m5'] > x['v5'] else 'same' if x['m5'] == x['v5'] else 'fewer'] += 1
                a['L0'] += x['L0']; a['Lv'] += x['Lv']; a['paid'] += x['paid']; a['pe'] += int(x['ate'] > 0)
                a['m5'] += x['m5']; a['v5'] += x['v5']
                a['edge'] += int(x['ov'] >= x['ev'])
                a['gain_m'] += x['mm'] + x['vm']; a['gain_v'] += x['mv'] + x['vv']
                a['drops'] += x['dm'] + x['dv']
                a['vq'] += x['vq']; a['mq'] += x['mq']; a['vtop8'] += int(x['vtop'] and x['Lv'] >= 8); a['vbig'] += int(x['vbig'] and x['Lv'] >= 5)
                a['v2x'] += int(x['Lv'] >= 2 * x['L0']); a['vlt'] += int(x['Lv'] < x['L0']); a['veq'] += int(x['Lv'] == x['L0'])
                a['vc'] += int(x['vc'] > 0); a['mut'] += int(x['mut'] > 0)
            print(' %s: n=%d (%.1f a game) | mover start length %.2f, victim %.2f | steps %.2f... paid a segment in %.3f, segments paid %.2f, ate on the way %.3f' % (
                lab, n, n / NG, a['L0'] / n, a['Lv'] / n, sum(x['k'] for g, x in S) / n, sum(1 for g, x in S if x['paid'] > 0) / n, a['paid'] / n, a['pe'] / n))
            print('   mover length  ', dist_line(cm, ['2', '3', '4', '5-7', '8-14', '15+']))
            print('   victim length ', dist_line(cv, ['2', '3', '4', '5-9', '10-19', '20+']))
            print('   steps to hit  ', dist_line(cd, ['1', '2', '3', '4+']))
            print('   segments paid ', dist_line(cp, ['0', '1', '2', '3+']))
            print('   other heads within 5 of the spot: mover side %.2f, victim side %.2f; mover side', a['m5'] / n, a['v5'] / n, dist_line(ce, ['more', 'same', 'fewer']), '| in the mover 7x7 view own>=enemy: %.3f' % (a['edge'] / n))
            print('   victim shorter %.3f, equal %.3f, at least twice the mover %.3f | victim a queen %.3f, mover a queen %.3f | victim its side longest and 8+ %.3f | victim (5+) longer than all of the mover side %.3f' % (
                a['vlt'] / n, a['veq'] / n, a['v2x'] / n, a['vq'] / n, a['mq'] / n, a['vtop8'] / n, a['vbig'] / n))
            print('   victim could have reached the mover at its own last turn %.3f | victim in reach of mover and mover in reach of victim (mutual) %.3f' % (a['vc'] / n, a['mut'] / n))
            print('   15 rounds later, per meeting: mover side lost %.2f and ate %.2f of the %.2f dropped (net %.2f); victim side lost %.2f and ate %.2f (net %.2f); swing to the mover side %.2f' % (
                a['L0'] / n, a['gain_m'] / n, a['drops'] / n, (a['gain_m'] - a['L0']) / n, a['Lv'] / n, a['gain_v'] / n, (a['gain_v'] - a['Lv']) / n,
                ((a['gain_m'] - a['L0']) - (a['gain_v'] - a['Lv'])) / n))
    # by class of (mover length, victim relation)
    print()
    print('== meetings by class: mover length x victim relation; per game; swing to the mover side per meeting ==')
    for ms, name in ((1, 'THEY'), (0, 'WE')):
        c = defaultdict(Counter)
        for g in G:
            for x in g['hos']:
                if not x['cross'] or x['ms'] != ms:
                    continue
                rel = 'q' if x['vq'] else 'lt' if x['Lv'] < x['L0'] else 'eq-2x' if x['Lv'] < 2 * x['L0'] else '2x<10' if x['Lv'] < 10 else '10+'
                k = (lc(x['L0']) if x['L0'] <= 4 else '5+', rel)
                a = c[k]
                a['n'] += 1; a['L0'] += x['L0']; a['Lv'] += x['Lv']; a['gm'] += x['mm'] + x['vm']; a['gv'] += x['mv'] + x['vv']; a['paid'] += int(x['paid'] > 0)
                a['fewer'] += int(x['m5'] < x['v5']); a['noedge'] += int(x['ov'] < x['ev'])
        for k in sorted(c):
            a = c[k]
            n = a['n']
            print(' %s mover %s victim %-6s: %6.2f a game | victim %.1f mover %.1f | paid %.2f | mover side fewer within 5: %.2f, outnumbered in view %.2f | mover net %.2f victim net %.2f swing %.2f' % (
                name, k[0], k[1], n / NG, a['Lv'] / n, a['L0'] / n, a['paid'] / n, a['fewer'] / n, a['noedge'] / n, (a['gm'] - a['L0']) / n, (a['gv'] - a['Lv']) / n,
                ((a['gm'] - a['L0']) - (a['gv'] - a['Lv'])) / n))


def rows():
    for g in G:
        for r in g['chs']:
            yield g, r


def ch_tables():
    print('== job 2: chances (dragon turn x enemy head in reach) ==')
    tot = Counter()
    for g, r in rows():
        tot[(r[1], 'n')] += 1
        tot[(r[1], 'took')] += int(r[22] == 1)
    for s, name in ((0, 'ours'), (1, 'theirs')):
        print(' %s: %.1f chances a game, taken %.3f' % (name, tot[(s, 'n')] / NG, tot[(s, 'took')] / max(1, tot[(s, 'n')])))

    def table(title, keyf, minn=300):
        c = defaultdict(Counter)
        for g, r in rows():
            k = keyf(g, r)
            if k is None:
                continue
            a = c[k]
            a[(r[1], 'n')] += 1
            a[(r[1], 'took')] += int(r[22] == 1)
        print()
        print(title)
        print('   class | ours: chances a game, take rate | theirs: chances a game, take rate | gap')
        for k in sorted(c):
            a = c[k]
            if a[(0, 'n')] + a[(1, 'n')] < minn:
                continue
            ro = a[(0, 'took')] / max(1, a[(0, 'n')])
            rt = a[(1, 'took')] / max(1, a[(1, 'n')])
            print('   %-28s | %7.2f %.3f | %7.2f %.3f | %+.3f' % (' '.join(str(z) for z in k), a[(0, 'n')] / NG, ro, a[(1, 'n')] / NG, rt, rt - ro))

    nq = lambda r: not r[4]
    paid = lambda r: 'pay' if r[10] > r[11] else 'free'
    rel = lambda r: 'queen' if r[8] else 'shorter' if r[7] < r[3] else 'eq-2x' if r[7] < 2 * r[3] else '2x<10' if r[7] < 10 else '10+'
    edge = lambda r: 'edge' if r[12] >= r[13] else 'outnum'
    ph = lambda g, r: phase(g, r[0], r[17] if r[1] == 0 else r[18])
    table('by actor length (queens apart)', lambda g, r: ('queen' if r[4] else lc(r[3]),))
    table('by phase (A before switch, B after, F full board feeding, C after the feed round), non-queen actors', lambda g, r: (ph(g, r),) if nq(r) else None)
    table('by free / paid, non-queen actors', lambda g, r: (paid(r),) if nq(r) else None)
    table('by target relation, non-queen actors', lambda g, r: (rel(r),) if nq(r) else None)
    table('by local count in the actor 7x7 view, non-queen actors', lambda g, r: (edge(r),) if nq(r) else None)
    table('actor length x target relation, non-queen', lambda g, r: (lc(r[3]) if r[3] <= 4 else '5+', rel(r)) if nq(r) else None)
    table('actor 2-4: target relation x pay x local count', lambda g, r: (rel(r), paid(r), edge(r)) if nq(r) and r[3] <= 4 else None)
    table('actor 2-4: phase x target relation', lambda g, r: (ph(g, r), rel(r)) if nq(r) and r[3] <= 4 else None)
    table('actor 2-4: phase x local count', lambda g, r: (ph(g, r), edge(r)) if nq(r) and r[3] <= 4 else None)
    table('actor 2-4: layout size x phase', lambda g, r: ('small' if g['aggr'] else 'big', ph(g, r)) if nq(r) and r[3] <= 4 else None)
    table('actor 5+: phase x target relation', lambda g, r: (ph(g, r), rel(r)) if nq(r) and r[3] > 4 else None)
    table('actor 5+ by own length x target relation', lambda g, r: (lc(r[3]), rel(r)) if nq(r) and r[3] > 4 else None)
    table('distance in steps, actor 2-4', lambda g, r: (min(r[10], 5),) if nq(r) and r[3] <= 4 else None)
    table('mutual reach (0 the target cannot reach back, 1 by paying, 2 free), actor 2-4', lambda g, r: (r[21],) if nq(r) and r[3] <= 4 else None)


def allowed(g, r):
    """Our code rule from the true state (main.cpp 2664-2702, 2603-2616, 2587-2598, 3680-3684). Returns the list of failing clauses."""
    rnd, L, q, Lt, tq, dist, free, ov, ev, vis, n_own, lng, big, pe = r[0], r[3], r[4], r[7], r[8], r[10], r[11], r[12], r[13], r[16], r[17], r[19], r[20], r[24]
    feeding = rnd > g['feed'] or (rnd > 200 and n_own >= 56)
    plain_reach = free + L - 2
    # hunt path first (no local count, any round): a head showing 10+ parts and own length + 4, by a dragon up to 10 long
    if not q and L <= 10 and dist - pe <= plain_reach and dist <= 8:
        if (vis >= 10 and vis >= L + 4) or big:
            return []
        if feeding and vis >= 6 and vis * 2 >= L and lng > 0:
            return []
    fails = []
    if q:
        fails.append('queen')
    if L > 4:
        fails.append('len>4')
    if rnd > g['feed']:
        fails.append('feedround')
    if n_own < (1 if g['aggr'] else 8):
        fails.append('units')
    if ov + 1 - ev < 1:
        fails.append('count')
    cap = n_own >= 59
    need = L if (cap or g['aggr']) else max(5, L + 2)
    if vis < need:
        fails.append('size')
    if dist > min(plain_reach, 3 if g['aggr'] else 4) or pe > 0 and dist > plain_reach:
        fails.append('steps')
    return fails


def rule_tables():
    print('== job 3: our rule (read from main.cpp, applied to the true state) against the chances ==')
    c = Counter()
    sole = Counter()
    anyf = Counter()
    for g, r in rows():
        f = allowed(g, r)
        s = r[1]
        took = int(r[22] == 1)
        c[(s, 'ok' if not f else 'no', 'n')] += 1
        c[(s, 'ok' if not f else 'no', 'took')] += took
        if f:
            for x in f:
                anyf[(s, x, 'n')] += 1
                anyf[(s, x, 'took')] += took
            if len(f) == 1:
                sole[(s, f[0], 'n')] += 1
                sole[(s, f[0], 'took')] += took
    for s, name in ((0, 'ours'), (1, 'theirs')):
        for k in ('ok', 'no'):
            print(' %s, rule says %s: %.2f chances a game, taken %.3f' % (name, k, c[(s, k, 'n')] / NG, c[(s, k, 'took')] / max(1, c[(s, k, 'n')])))
    print(' clause | fails (any): ours a game, our take, theirs a game, their take | the only failing clause: ours a game, our take, theirs a game, their take')
    for x in ('queen', 'len>4', 'feedround', 'units', 'count', 'size', 'steps'):
        print('  %-10s | %7.2f %.3f %7.2f %.3f | %7.2f %.3f %7.2f %.3f' % (
            x, anyf[(0, x, 'n')] / NG, anyf[(0, x, 'took')] / max(1, anyf[(0, x, 'n')]), anyf[(1, x, 'n')] / NG, anyf[(1, x, 'took')] / max(1, anyf[(1, x, 'n')]),
            sole[(0, x, 'n')] / NG, sole[(0, x, 'took')] / max(1, sole[(0, x, 'n')]), sole[(1, x, 'n')] / NG, sole[(1, x, 'took')] / max(1, sole[(1, x, 'n')])))
    # our take rate where the rule says ok, by phase and whether a longer own dragon is in view
    print(' rule says ok, ours, by phase and a longer own head in view now (after the switch a dragon that knows no longer one is its own leader):')
    c2 = defaultdict(Counter)
    for g, r in rows():
        if r[1] != 0 or allowed(g, r):
            continue
        k = (phase(g, r[0], r[17]), 'longer in view' if r[19] else 'none in view', 'len<=4' if r[3] <= 4 else 'len 5-10')
        c2[k]['n'] += 1
        c2[k]['took'] += int(r[22] == 1)
    for k in sorted(c2):
        print('   %-40s %7.2f a game, taken %.3f' % (' '.join(k), c2[k]['n'] / NG, c2[k]['took'] / c2[k]['n']))


sec = sys.argv[1] if len(sys.argv) > 1 else 'all'
if sec in ('ho', 'all'):
    ho_tables()
if sec in ('ch', 'all'):
    ch_tables()
if sec in ('rule', 'all'):
    rule_tables()

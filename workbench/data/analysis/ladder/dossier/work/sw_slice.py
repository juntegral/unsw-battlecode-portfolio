# Scratch (sweep brief): slices of dossier/per-game.jsonl. No replay is opened here.
import json
import math
from collections import defaultdict

PATH = 'data/analysis/ladder/dossier/per-game.jsonl'
KEEP = ('pearls_eaten', 'splits', 'turns', 'no_view_pearl_turns', 'no_view_pearl_moved', 'keeps_eligible', 'keeps',
        'dither', 'adjacent_pearl_turns', 'adjacent_pearl_missed', 'hot_turns', 'seen_share_end', 'end_state',
        'no_view_pearl_distinct_per_dragon_20', 'distinct_per_dragon_20', 'births', 'near6_births')
games = defaultdict(dict)
with open(PATH) as f:
    for line in f:
        r = json.loads(line)
        slim = {k: r[k] for k in ('game', 'layout_key', 'opponent_rating', 'relation', 'our_result', 'cells', 'last_round')}
        slim['starts'] = len(r['starting_dragons'])
        slim['startlen'] = r['starting_dragons'][0]['length']
        slim['ranges'] = {name: {k: rr.get(k) for k in KEEP} for name, rr in r['ranges'].items()}
        games[r['game']][r['relation']] = slim
G = [g for g in games.values() if 'us' in g and 'them' in g]
print('games', len(G))

def band(x):
    return '<1900' if x < 1900 else ('1900-2099' if x < 2100 else '2100+')

def pooled(sel, rng, num, den):
    out = []
    for side in ('us', 'them'):
        n = sum(g[side]['ranges'][rng][num] or 0 for g in sel)
        d = sum(g[side]['ranges'][rng][den] or 0 for g in sel)
        out.append((n, d))
    return out

def fmt(pair):
    return ' / '.join('%.1f%% (%d of %d)' % (100.0 * n / d if d else float('nan'), n, d) for n, d in pair)

TD = 'Tower Defense #1'
PD = ('Prisoners Dilemma #1', 'Prisoners Dilemma #2')
print('\n== 1. pooled dither and keeps, r0-100, ours / theirs')
sets = {'all': G, 'without TD': [g for g in G if g['us']['layout_key'] != TD],
        'without TD and both PD': [g for g in G if g['us']['layout_key'] != TD and g['us']['layout_key'] not in PD]}
for name, sel in sets.items():
    print(name, len(sel), 'dither', fmt(pooled(sel, '0-100', 'dither', 'no_view_pearl_moved')))
    print(name, len(sel), 'keeps ', fmt(pooled(sel, '0-100', 'keeps', 'keeps_eligible')))
for b in ('<1900', '1900-2099', '2100+'):
    for name, sel in sets.items():
        s = [g for g in sel if band(g['us']['opponent_rating']) == b]
        print(b, name, len(s), 'dither', fmt(pooled(s, '0-100', 'dither', 'no_view_pearl_moved')))
for rng in ('0-50', '51-100', '101-300'):
    for name, sel in sets.items():
        print(rng, name, 'dither', fmt(pooled(sel, rng, 'dither', 'no_view_pearl_moved')))

print('\n== 2. how much of the turn budget this is, r0-100 (ours / theirs)')
for name, sel in sets.items():
    print(name, 'no-pearl turns of all turns', fmt(pooled(sel, '0-100', 'no_view_pearl_turns', 'turns')))
    print(name, 'dither turns of all turns ', fmt(pooled(sel, '0-100', 'dither', 'turns')))
    print(name, 'hot turns of all turns    ', fmt(pooled(sel, '0-100', 'hot_turns', 'turns')))

print('\n== 3. per layout, r0-100: games in which our dither share is the higher one (both sides 10+ blind moved turns)')
lay = defaultdict(list)
for g in G:
    lay[g['us']['layout_key']].append(g)
tot = [0, 0, 0]
for L in sorted(lay):
    hi = lo = eq = 0
    for g in lay[L]:
        a, b = g['us']['ranges']['0-100'], g['them']['ranges']['0-100']
        if a['no_view_pearl_moved'] < 10 or b['no_view_pearl_moved'] < 10:
            continue
        x, y = a['dither'] / a['no_view_pearl_moved'], b['dither'] / b['no_view_pearl_moved']
        if x > y:
            hi += 1
        elif x < y:
            lo += 1
        else:
            eq += 1
    tot[0] += hi; tot[1] += lo; tot[2] += eq
    p = pooled(lay[L], '0-100', 'dither', 'no_view_pearl_moved')
    h = pooled(lay[L], '0-100', 'hot_turns', 'turns')
    k = pooled(lay[L], '0-100', 'keeps', 'keeps_eligible')
    print('%-22s n=%2d ours higher %2d lower %2d | dither %5.1f/%5.1f keeps %5.1f/%5.1f hot %5.1f/%5.1f' % (
        L, len(lay[L]), hi, lo, 100 * p[0][0] / max(1, p[0][1]), 100 * p[1][0] / max(1, p[1][1]),
        100 * k[0][0] / max(1, k[0][1]), 100 * k[1][0] / max(1, k[1][1]),
        100 * h[0][0] / max(1, h[0][1]), 100 * h[1][0] / max(1, h[1][1])))
print('games: ours higher', tot[0], 'lower', tot[1], 'equal', tot[2])

def pear(xs, ys):
    n = len(xs)
    if n < 3:
        return float('nan')
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs); syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return float('nan')
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sxx * syy)

def within(fx, fy, sel=None, z=False):
    xs, ys = [], []
    used = 0
    for L in lay:
        pts = []
        for g in lay[L]:
            if sel is not None and not sel(g):
                continue
            x, y = fx(g), fy(g)
            if x is None or y is None:
                continue
            pts.append((x, y))
        if len(pts) < 4:
            continue
        mx = sum(p[0] for p in pts) / len(pts); my = sum(p[1] for p in pts) / len(pts)
        sx = math.sqrt(sum((p[0] - mx) ** 2 for p in pts) / len(pts)) or 1.0
        sy = math.sqrt(sum((p[1] - my) ** 2 for p in pts) / len(pts)) or 1.0
        for p in pts:
            xs.append((p[0] - mx) / (sx if z else 1.0)); ys.append((p[1] - my) / (sy if z else 1.0))
        used += 1
    return pear(xs, ys), len(xs), used

def share(side, rng, num, den, floor=10):
    def f(g):
        r = g[side]['ranges'][rng]
        if (r[den] or 0) < floor:
            return None
        return r[num] / r[den]
    return f

def val(side, rng, key):
    def f(g):
        return g[side]['ranges'][rng][key]
    return f

def pshare(rng):
    def f(g):
        a = g['us']['ranges'][rng]['pearls_eaten']; b = g['them']['ranges'][rng]['pearls_eaten']
        return a / (a + b) if a + b >= 10 else None
    return f

def lenshare(g):
    a = g['us']['ranges']['0-100']['end_state']; b = g['them']['ranges']['0-100']['end_state']
    if not a or not b or a.get('total') is None or b.get('total') is None or a['total'] + b['total'] == 0:
        return None
    return a['total'] / (a['total'] + b['total'])

def won(g):
    return 1.0 if g['us']['our_result'] == 'win' else (0.0 if g['us']['our_result'] == 'loss' else None)

def gap(f1, f2):
    def f(g):
        a, b = f1(g), f2(g)
        return None if a is None or b is None else a - b
    return f

def npd(side, rng):
    def f(g):
        d = g[side]['ranges'][rng]['no_view_pearl_distinct_per_dragon_20']
        return d['mean'] if d and d.get('n') else None
    return f

X = {
    'our dither 0-100': share('us', '0-100', 'dither', 'no_view_pearl_moved'),
    'our dither 0-50': share('us', '0-50', 'dither', 'no_view_pearl_moved'),
    'dither gap (ours-theirs) 0-100': gap(share('us', '0-100', 'dither', 'no_view_pearl_moved'), share('them', '0-100', 'dither', 'no_view_pearl_moved')),
    'our keeps 0-100': share('us', '0-100', 'keeps', 'keeps_eligible'),
    'our keeps 0-50': share('us', '0-50', 'keeps', 'keeps_eligible'),
    'keeps gap 0-100': gap(share('us', '0-100', 'keeps', 'keeps_eligible'), share('them', '0-100', 'keeps', 'keeps_eligible')),
    'our blind distinct per 20 0-100': npd('us', '0-100'),
    'our seen share at r100': val('us', '0-100', 'seen_share_end'),
    'our seen share at r50': val('us', '0-50', 'seen_share_end'),
    'our hot 0-100': share('us', '0-100', 'hot_turns', 'turns'),
    'our hot 0-50': share('us', '0-50', 'hot_turns', 'turns'),
    'their hot 0-100': share('them', '0-100', 'hot_turns', 'turns'),
    'hot gap (ours-theirs) 0-100': gap(share('us', '0-100', 'hot_turns', 'turns'), share('them', '0-100', 'hot_turns', 'turns')),
    'hot gap 0-50': gap(share('us', '0-50', 'hot_turns', 'turns'), share('them', '0-50', 'hot_turns', 'turns')),
    'hot gap 51-100': gap(share('us', '51-100', 'hot_turns', 'turns'), share('them', '51-100', 'hot_turns', 'turns')),
    'our adjacent miss 0-100': share('us', '0-100', 'adjacent_pearl_missed', 'adjacent_pearl_turns'),
}
Y = {
    'our pearls 0-100': val('us', '0-100', 'pearls_eaten'),
    'pearl share 0-100': pshare('0-100'),
    'pearl share 51-100': pshare('51-100'),
    'pearl share 101-300': pshare('101-300'),
    'length share r100': lenshare,
    'won': won,
}
print('\n== 4. within-layout Pearson, layout mean removed (raw | z-scored inside layout), N, layouts')
for xn, fx in X.items():
    cells = []
    for yn, fy in Y.items():
        r1, n, k = within(fx, fy)
        r2, _, _ = within(fx, fy, z=True)
        cells.append('%s %+.2f|%+.2f (N=%d)' % (yn, r1, r2, n))
    print('%-32s' % xn, '; '.join(cells))
print('same, without TD:')
noTD = lambda g: g['us']['layout_key'] != TD
for xn in ('our dither 0-100', 'our dither 0-50', 'our keeps 0-100', 'dither gap (ours-theirs) 0-100', 'keeps gap 0-100', 'our hot 0-100', 'hot gap (ours-theirs) 0-100', 'hot gap 0-50'):
    cells = []
    for yn, fy in Y.items():
        r2, n, _ = within(X[xn], fy, sel=noTD, z=True)
        cells.append('%s %+.2f (N=%d)' % (yn, r2, n))
    print('%-32s' % xn, '; '.join(cells))

print('\n== 5. lag: does the r0-50 measure go with the r51-100 pearl share once the r0-50 pearl share is taken out (z inside layout, residual on residual)')
def partial(fx, fy, fc, sel=None):
    xs, ys, cs = [], [], []
    for L in lay:
        pts = []
        for g in lay[L]:
            if sel is not None and not sel(g):
                continue
            t = (fx(g), fy(g), fc(g))
            if None in t:
                continue
            pts.append(t)
        if len(pts) < 5:
            continue
        for i, dst in enumerate((xs, ys, cs)):
            m = sum(p[i] for p in pts) / len(pts)
            s = math.sqrt(sum((p[i] - m) ** 2 for p in pts) / len(pts)) or 1.0
            dst.extend((p[i] - m) / s for p in pts)
    rxy, rxc, ryc = pear(xs, ys), pear(xs, cs), pear(ys, cs)
    den = math.sqrt(max(1e-12, (1 - rxc ** 2) * (1 - ryc ** 2)))
    return (rxy - rxc * ryc) / den, rxy, len(xs)
for xn in ('our dither 0-50', 'our keeps 0-50', 'our hot 0-50', 'hot gap 0-50', 'our seen share at r50'):
    for yn in ('pearl share 51-100', 'pearl share 101-300'):
        p, r, n = partial(X[xn], Y[yn], pshare('0-50'))
        print('%-24s -> %-20s plain %+.2f, with r0-50 pearl share held %+.2f (N=%d)' % (xn, yn, r, p, n))

print('\n== 6. halves inside each layout (our measure below or above the layout median), r0-100: mean pearls, pearl share, wins')
def halves(fx, label, sel=None):
    acc = {'low': [0, 0.0, 0.0, 0, 0], 'high': [0, 0.0, 0.0, 0, 0]}
    more = [0, 0]
    for L in lay:
        pts = [(fx(g), g) for g in lay[L] if (sel is None or sel(g)) and fx(g) is not None and Y['pearl share 0-100'](g) is not None]
        if len(pts) < 6:
            continue
        pts.sort(key=lambda t: t[0])
        h = len(pts) // 2
        grp = {'low': pts[:h], 'high': pts[len(pts) - h:]}
        mean = {}
        for k, part in grp.items():
            a = acc[k]
            for _, g in part:
                a[0] += 1; a[1] += g['us']['ranges']['0-100']['pearls_eaten']; a[2] += Y['pearl share 0-100'](g)
                a[3] += 1 if g['us']['our_result'] == 'win' else 0; a[4] += 1 if g['us']['our_result'] in ('win', 'loss') else 0
            mean[k] = sum(Y['pearl share 0-100'](g) for _, g in part) / len(part)
        more[0 if mean['low'] > mean['high'] else 1] += 1
    for k in ('low', 'high'):
        a = acc[k]
        print('%-28s %-4s games %3d pearls %6.1f pearl share %.3f won %d of %d' % (label, k, a[0], a[1] / max(1, a[0]), a[2] / max(1, a[0]), a[3], a[4]))
    print('%-28s layouts where the LOW half has the higher pearl share: %d, the HIGH half: %d' % (label, more[0], more[1]))
halves(X['our dither 0-100'], 'our dither 0-100')
halves(X['our dither 0-50'], 'our dither 0-50')
halves(X['our keeps 0-100'], 'our keeps 0-100')
halves(X['our hot 0-100'], 'our hot 0-100')
halves(X['our hot 0-50'], 'our hot 0-50')
halves(X['hot gap (ours-theirs) 0-100'], 'hot gap 0-100')
halves(X['our blind distinct per 20 0-100'], 'our blind distinct/20')

print('\n== 7. behind in total length at r100 (share under 0.45) against not: pooled dither, keeps, hot, r0-100, ours / theirs')
for name, cond in (('behind', lambda s: s < 0.45), ('not behind', lambda s: s >= 0.45)):
    for sname, sel in (('all', G), ('without TD', sets['without TD'])):
        s = [g for g in sel if lenshare(g) is not None and cond(lenshare(g))]
        lost = sum(1 for g in s if g['us']['our_result'] == 'loss')
        print(name, sname, len(s), 'lost', lost, '| dither', fmt(pooled(s, '0-100', 'dither', 'no_view_pearl_moved')))
        print(name, sname, len(s), '| keeps', fmt(pooled(s, '0-100', 'keeps', 'keeps_eligible')), '| hot', fmt(pooled(s, '0-100', 'hot_turns', 'turns')))

print('\n== 8. blind distinct tiles per dragon per 20 rounds and board seen, pooled over games (ours / theirs), layouts where ours is higher')
cnt = {'npd': [0, 0], 'seen': [0, 0], 'hot': [0, 0], 'dither': [0, 0], 'keeps': [0, 0]}
for L in sorted(lay):
    def m(side, f):
        v = [f(g) for g in lay[L]]
        v = [x for x in v if x is not None]
        return sum(v) / len(v) if v else float('nan')
    a, b = m('us', npd('us', '0-100')), m('them', npd('them', '0-100'))
    c, d = m('us', val('us', '0-100', 'seen_share_end')), m('them', val('them', '0-100', 'seen_share_end'))
    cnt['npd'][0 if a > b else 1] += 1
    cnt['seen'][0 if c > d else 1] += 1
    for key, num, den in (('hot', 'hot_turns', 'turns'), ('dither', 'dither', 'no_view_pearl_moved'), ('keeps', 'keeps', 'keeps_eligible')):
        p = pooled(lay[L], '0-100', num, den)
        cnt[key][0 if p[0][0] / max(1, p[0][1]) > p[1][0] / max(1, p[1][1]) else 1] += 1
print('layouts ours higher / theirs higher:', cnt)

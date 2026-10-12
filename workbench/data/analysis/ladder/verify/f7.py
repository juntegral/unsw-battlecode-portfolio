import sys, json, math, random
from pathlib import Path
from collections import Counter, defaultdict
from statistics import median
from datetime import datetime, timedelta
sys.dont_write_bytecode = True
V = Path('data/analysis/ladder/verify')


def load():
    games = []
    for k in range(4):
        for line in (V / ('shard%d.jsonl' % k)).read_text().splitlines():
            games.append(json.loads(line))
    order = sorted(games, key=lambda g: (g['completedAt'], g['game']))
    seen = {}
    for g in order:
        lst = seen.setdefault(g['map'], [])
        if g['layout'] not in lst:
            lst.append(g['layout'])
        g['map_key'] = '%s #%d' % (g['map'], lst.index(g['layout']) + 1)
        e = g['opponentElo']
        g['band'] = '<1700' if e < 1700 else '1700-1899' if e < 1900 else '1900-2099' if e < 2100 else '2100+'
        g['evening'] = (datetime.fromisoformat(g['at_kst']) - timedelta(hours=6)).strftime('%m-%d')
        g['opp'] = '%s (%s)' % (g['opponent'], g['opponentId'])
    main = [g for g in order if g['main']]
    for z, g in enumerate(main):
        g['half'] = 'first' if z < 97 else 'second'
    return games, main


def fisher(a, b, c, d):
    n = a + b + c + d
    r1 = a + b
    c1 = a + c

    def pr(x):
        return math.comb(r1, x) * math.comb(n - r1, c1 - x) / math.comb(n, c1)
    p0 = pr(a)
    return sum(pr(x) for x in range(max(0, c1 - (n - r1)), min(r1, c1) + 1) if pr(x) <= p0 * (1 + 1e-9))


def sign(k, n):
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2 ** n)


def boot(gs, f, n=2000, seed=1):
    rng = random.Random(seed)
    bt = defaultdict(list)
    for g in gs:
        bt[g['battle']].append(g)
    keys = sorted(bt)
    vals = []
    for _ in range(n):
        sample = []
        for _k in keys:
            sample.extend(bt[rng.choice(keys)])
        v = f(sample)
        if v is not None:
            vals.append(v)
    vals.sort()
    return round(vals[int(0.025 * len(vals))], 3), round(vals[int(0.975 * len(vals)) - 1], 3)


def group(gs, key):
    out = defaultdict(list)
    for g in gs:
        out[g[key]].append(g)
    return out


P = '~/01. Project/\u1100\u1162\u110b\u1175\u11ab \u1111\u1173\u1105\u1169\u110c\u1166\u11a8\u1110\u1173/unsw-swarm/data/analysis/ladder/verify/'
OUT = []


def say(*a):
    OUT.append(' '.join(str(x) for x in a))


games, main = load()
say('main games', len(main), 'by bot', dict(Counter(g['bot'] for g in main)))
two = [g for g in main if g['start']['us'] == 2 and g['start']['them'] == 2]
two_ids = set(g['game'] for g in two)
other = [g for g in main if g['game'] not in two_ids]
say('start dragons per layout (main):', sorted(set((g['map_key'], g['start']['us'], g['start']['them']) for g in main)))


def reached(g):
    return g['last_round'] >= 100


def stall(g, a=6, b=15, r='100'):
    m = g['marks'].get(r)
    return m is not None and m['us']['alive'] <= a and m['them']['alive'] >= b


def rev(g, a=6, b=15, r='100'):
    m = g['marks'].get(r)
    return m is not None and m['them']['alive'] <= a and m['us']['alive'] >= b


tr = [g for g in two if reached(g)]
orr = [g for g in other if reached(g)]
say('2-start main games', len(two), 'reached r100', len(tr), '| ended before r100:', [(g['game'], g['map_key'], g['last_round'], 'win' if g['win'] else 'loss') for g in two if not reached(g)])
say('other-layout main games', len(other), 'reached r100', len(orr), '| ended before r100:', [(g['game'], g['map_key'], g['last_round'], 'win' if g['win'] else 'loss') for g in other if not reached(g)])
st = [g for g in tr if stall(g)]
say('STALL', len(st), 'of', len(tr), 'wins', sum(g['win'] for g in st))
for g in st:
    m = g['marks']['100']
    say('  ', g['game'], g['map_key'], g['opp'], g['opponentElo'], g['band'], g['evening'], g['half'], 'alive', m['us']['alive'], m['them']['alive'], 'total', m['us']['total'], m['them']['total'], 'pearls0-100', g['pearls_0_100']['us'], g['pearls_0_100']['them'], 'win' if g['win'] else 'loss', 'last', g['last_round'], 'bot', g['bot'])
for b in ('<1700', '1700-1899', '1900-2099', '2100+'):
    bg = [g for g in tr if g['band'] == b]
    say('band', b, 'stall', sum(stall(g) for g in bg), 'of', len(bg), '| reverse', sum(rev(g) for g in bg))
say('reverse (them<=6, us>=15) on 2-start', sum(rev(g) for g in tr), [(g['game'], g['map_key'], g['opp'], 'win' if g['win'] else 'loss') for g in tr if rev(g)])
say('other layouts: stall', sum(stall(g) for g in orr), 'of', len(orr), 'reverse', sum(rev(g) for g in orr))
say('stall median pearls r0-100 us', median(g['pearls_0_100']['us'] for g in st), 'them', median(g['pearls_0_100']['them'] for g in st))
say('non-stall 2-start median pearls r0-100 us', median(g['pearls_0_100']['us'] for g in tr if not stall(g)), 'them', median(g['pearls_0_100']['them'] for g in tr if not stall(g)))
say('by layout (stall/reached/wins all reached):')
for k, gs in sorted(group(tr, 'map_key').items()):
    say('  ', k, sum(stall(g) for g in gs), 'of', len(gs), 'reverse', sum(rev(g) for g in gs), 'wins', sum(g['win'] for g in gs))
say('by opponent (2-start reached):')
for k, gs in sorted(group(tr, 'opp').items(), key=lambda kv: -sum(stall(g) for g in kv[1])):
    if sum(stall(g) for g in gs) or len(gs) >= 5:
        say('  ', k, 'elo', sorted(set(g['opponentElo'] for g in gs)), 'stall', sum(stall(g) for g in gs), 'of', len(gs))
say('by evening:', {k: '%d of %d' % (sum(stall(g) for g in gs), len(gs)) for k, gs in sorted(group(tr, 'evening').items())})
say('by half:', {k: '%d of %d' % (sum(stall(g) for g in gs), len(gs)) for k, gs in sorted(group(tr, 'half').items())})
say('by bot id:', {k: '%d of %d' % (sum(stall(g) for g in gs), len(gs)) for k, gs in sorted(group(tr, 'bot').items())})
say('battles with a stall', len(set(g['battle'] for g in st)), 'of', len(set(g['battle'] for g in tr)))
ns = [g for g in tr if not stall(g)]
say('wins: stall', sum(g['win'] for g in st), '/', len(st), ' non-stall 2-start', sum(g['win'] for g in ns), '/', len(ns), 'fisher p', fisher(sum(g['win'] for g in st), len(st) - sum(g['win'] for g in st), sum(g['win'] for g in ns), len(ns) - sum(g['win'] for g in ns)))
say('2-start vs other fisher p', fisher(len(st), len(tr) - len(st), sum(stall(g) for g in orr), len(orr) - sum(stall(g) for g in orr)))
# win rate by band in non-stall
for b in ('1700-1899', '1900-2099', '2100+'):
    bg = [g for g in tr if g['band'] == b]
    say('  band', b, 'wins all', sum(g['win'] for g in bg), '/', len(bg), 'stall wins', sum(g['win'] for g in bg if stall(g)), '/', sum(stall(g) for g in bg))
say('threshold grid at r100: (ours<=a, theirs>=b): 2-start stall/reverse | other stall/reverse')
for a in (4, 6, 8, 10):
    for b in (10, 12, 15, 20):
        say('  a=%d b=%d: %d/%d | %d/%d' % (a, b, sum(stall(g, a, b) for g in tr), sum(rev(g, a, b) for g in tr), sum(stall(g, a, b) for g in orr), sum(rev(g, a, b) for g in orr)))
for r in ('50', '100', '150', '200'):
    def rel(g, sw=False):
        m = g['marks'].get(r)
        if m is None:
            return False
        u, t = m['us']['alive'], m['them']['alive']
        if sw:
            u, t = t, u
        return t >= 15 and t >= 2.5 * u
    say('ratio rule r%s (theirs>=15 and >=2.5x ours): 2-start %d (reverse %d) of %d | other %d (reverse %d) of %d' % (r, sum(rel(g) for g in two), sum(rel(g, True) for g in two), sum(1 for g in two if r in g['marks']), sum(rel(g) for g in other), sum(rel(g, True) for g in other), sum(1 for g in other if r in g['marks'])))
say('other layouts at r100: our alive min/median/max', min(g['marks']['100']['us']['alive'] for g in orr), median(g['marks']['100']['us']['alive'] for g in orr), max(g['marks']['100']['us']['alive'] for g in orr), 'games with ours<=6:', sum(1 for g in orr if g['marks']['100']['us']['alive'] <= 6), 'of those theirs max', max([g['marks']['100']['them']['alive'] for g in orr if g['marks']['100']['us']['alive'] <= 6], default=None))
say('other layouts by layout: ours<=6 at r100 / theirs>=15 at r100 / n')
for k, gs in sorted(group(orr, 'map_key').items()):
    say('  ', k, 'start', gs[0]['start']['us'], sum(1 for g in gs if g['marks']['100']['us']['alive'] <= 6), sum(1 for g in gs if g['marks']['100']['them']['alive'] >= 15), len(gs), 'median alive us/them', median(g['marks']['100']['us']['alive'] for g in gs), median(g['marks']['100']['them']['alive'] for g in gs))
say('2-start by layout: median alive r100 us/them')
for k, gs in sorted(group(tr, 'map_key').items()):
    say('  ', k, median(g['marks']['100']['us']['alive'] for g in gs), median(g['marks']['100']['them']['alive'] for g in gs), 'ours<=6:', sum(1 for g in gs if g['marks']['100']['us']['alive'] <= 6), 'theirs<=6:', sum(1 for g in gs if g['marks']['100']['them']['alive'] <= 6), 'n', len(gs))
# drop the three strongest stall games (largest theirs - ours)
top = sorted(st, key=lambda g: -(g['marks']['100']['them']['alive'] - g['marks']['100']['us']['alive']))[:3]
say('three strongest stall games', [(g['game'], g['map_key'], g['marks']['100']['us']['alive'], g['marks']['100']['them']['alive']) for g in top], '-> remaining', len(st) - 3, 'of', len(tr) - 3, 'vs other 0 of', len(orr), 'fisher p', fisher(len(st) - 3, len(tr) - len(st), 0, len(orr)))
for k in sorted(set(g['opp'] for g in st)):
    rest = [g for g in tr if g['opp'] != k]
    say('  without', k, ':', sum(stall(g) for g in rest), 'of', len(rest), 'wins among stalls', sum(g['win'] for g in rest if stall(g)))
for k in sorted(set(g['map_key'] for g in st)):
    rest = [g for g in tr if g['map_key'] != k]
    say('  without', k, ':', sum(stall(g) for g in rest), 'of', len(rest))
for k in sorted(set(g['evening'] for g in st)):
    rest = [g for g in tr if g['evening'] != k]
    say('  without evening', k, ':', sum(stall(g) for g in rest), 'of', len(rest))

say()
say('PART B')
td = [g for g in main if g['map_key'] == 'Tower Defense #1' and reached(g)]
say('Tower Defense #1 main games', sum(1 for g in main if g['map_key'] == 'Tower Defense #1'), 'reached r100', len(td))


def pm(g, z, lo=0, hi=50):
    vals = [g['partb'][str(r)][z] for r in range(lo, hi + 1)]
    none = sum(1 for v in vals if v is None)
    return median([v if v is not None else 10 ** 6 for v in vals]), none


for g in td:
    mu, nu = pm(g, 0)
    mt, nt = pm(g, 1)
    r0 = g['partb']['0']
    r50 = g['partb']['50']
    say('  ', g['game'], g['opp'], 'stall' if stall(g) else '-', 'win' if g['win'] else 'loss', 'path med us', mu, 'them', mt, 'none', nu, nt, '| r0 path', r0[0], r0[1], 'pearls on board', r0[4], '| r50 heads', r50[2], r50[3], '| pearls0-100', g['pearls_0_100']['us'], g['pearls_0_100']['them'], '| alive100', g['marks']['100']['us']['alive'], g['marks']['100']['them']['alive'])
    say('      us  path every 5 rounds', [g['partb'][str(r)][0] for r in range(0, 51, 5)], 'heads', [g['partb'][str(r)][2] for r in range(0, 51, 5)])
    say('      them path every 5 rounds', [g['partb'][str(r)][1] for r in range(0, 51, 5)], 'heads', [g['partb'][str(r)][3] for r in range(0, 51, 5)])
sg = [g for g in td if stall(g)]
og = [g for g in td if not stall(g)]
say('median over games: ours all', median(pm(g, 0)[0] for g in td), '| ours in stall', median(pm(g, 0)[0] for g in sg), '| ours in other', median(pm(g, 0)[0] for g in og))
say('theirs all', median(pm(g, 1)[0] for g in td), '| theirs in stall (%d games)' % len(sg), median(pm(g, 1)[0] for g in sg), '| theirs in other (%d games)' % len(og), median(pm(g, 1)[0] for g in og))
say('pearls r0-100 median: ours all', median(g['pearls_0_100']['us'] for g in td), 'ours stall', median(g['pearls_0_100']['us'] for g in sg), 'ours other', median(g['pearls_0_100']['us'] for g in og), '| theirs stall', median(g['pearls_0_100']['them'] for g in sg), 'theirs other', median(g['pearls_0_100']['them'] for g in og))
say('rounds 0-10 only (both sides still have their starting heads): ours', median(pm(g, 0, 0, 10)[0] for g in td), 'theirs stall', median(pm(g, 1, 0, 10)[0] for g in sg), 'theirs other', median(pm(g, 1, 0, 10)[0] for g in og))
say('rounds 0-20: ours', median(pm(g, 0, 0, 20)[0] for g in td), 'theirs stall', median(pm(g, 1, 0, 20)[0] for g in sg), 'theirs other', median(pm(g, 1, 0, 20)[0] for g in og))
say('first round their path < our path, per game:', [(g['game'], next((r for r in range(51) if g['partb'][str(r)][1] is not None and g['partb'][str(r)][0] is not None and g['partb'][str(r)][1] < g['partb'][str(r)][0]), None)) for g in td])
say('their head count when their path first drops below 20:', [(g['game'], next(((r, g['partb'][str(r)][3]) for r in range(51) if g['partb'][str(r)][1] is not None and g['partb'][str(r)][1] < 20), None)) for g in td])
say('first round each side ate a pearl is not stored; pearls eaten r0-50 (marks 50):', [(g['game'], g['marks']['50']['us']['pearls'], g['marks']['50']['them']['pearls']) for g in td])
say('same measure on the other 2-start layouts (median over games of per-game median path, us / them; stall vs other):')
for k, gs in sorted(group(tr, 'map_key').items()):
    s1 = [g for g in gs if stall(g)]
    o1 = [g for g in gs if not stall(g)]
    say('  ', k, 'stall n', len(s1), [median(pm(g, z)[0] for g in s1) if s1 else None for z in (0, 1)], 'other n', len(o1), [median(pm(g, z)[0] for g in o1) if o1 else None for z in (0, 1)], 'r0 path us/them', sorted(set((g['partb']['0'][0], g['partb']['0'][1]) for g in gs), key=str)[:4])

Path(P + 'f7-numbers.txt').write_text('\n'.join(OUT) + '\n')

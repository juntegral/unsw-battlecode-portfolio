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
    if not vals:
        return (None, None)
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

def credit(gs, drop_sides=('us', 'them'), pred=None):
    us = them = drop = 0
    for g in gs:
        for m in g['meetings']:
            if pred is not None and not pred(m):
                continue
            for s in drop_sides:
                us += m['w15'][s]['us']
                them += m['w15'][s]['them']
                drop += m['drop'][s]
    return us, them, drop


def share(gs):
    u, t, d = credit(gs)
    return u / (u + t) if u + t else None


def line(name, gs):
    u, t, d = credit(gs)
    say(name, 'games', len(gs), 'us', u, 'them', t, 'dropped', d, 'share', round(u / (u + t), 4) if u + t else None, 'battle bootstrap 95%', boot(gs, share, 1000))


say('main games', len(main), 'meetings', sum(len(g['meetings']) for g in main), 'same-team head-ons', sum(g['same_team_head_on'] for g in main), 'games without a cross-team meeting', sum(1 for g in main if not g['meetings']))
line('ALL', main)
for b in ('<1700', '1700-1899', '1900-2099', '2100+'):
    line('band ' + b, [g for g in main if g['band'] == b])
for h in ('first', 'second'):
    line('half ' + h, [g for g in main if g['half'] == h])
fewer = sum(1 for g in main if credit([g])[0] < credit([g])[1])
more = sum(1 for g in main if credit([g])[0] > credit([g])[1])
say('games fewer / more / equal', fewer, more, len(main) - fewer - more, 'sign test p', sign(more, fewer + more))
tot = Counter()
for g in main:
    for m in g['meetings']:
        for s in ('us', 'them'):
            tot['later'] += m['later'][s]
            tot['never'] += m['never'][s]
            tot['censored'] += m['censored'][s]
say('not credited: eaten later than 15 rounds', tot['later'], 'never eaten', tot['never'], 'censored by game end', tot['censored'])
for s in ('us', 'them'):
    u, t, d = credit(main, (s,))
    say('pearls dropped by', s, ':', d, 'eaten within 15 by us', u, 'by them', t, 'our share', round(u / (u + t), 4))
for a in ('us', 'them'):
    u, t, d = credit(main, pred=lambda m: m['actor_side'] == a)
    say('meetings where the mover was', a, ': count', sum(1 for g in main for m in g['meetings'] if m['actor_side'] == a), 'us', u, 'them', t, 'share', round(u / (u + t), 4))
pu = sum(g['pearls_all']['us'] for g in main)
pt = sum(g['pearls_all']['them'] for g in main)
nu = sum(g['eat_origin']['us'].get('natural', 0) for g in main)
nt = sum(g['eat_origin']['them'].get('natural', 0) for g in main)
du = sum(g['eat_origin']['us'].get('drop', 0) for g in main)
dt = sum(g['eat_origin']['them'].get('drop', 0) for g in main)
tu = sum(g['turns'].get('us', 0) for g in main)
tt = sum(g['turns'].get('them', 0) for g in main)
say('all pearls eaten, whole game: us', pu, 'them', pt, 'share', round(pu / (pu + pt), 4), '| natural only', nu, nt, round(nu / (nu + nt), 4), '| every death drop', du, dt, round(du / (du + dt), 4), '| dragon turns', tu, tt, round(tu / (tu + tt), 4))
u, t, d = credit(main)
other_u = du - sum(m['w15'][s]['us'] for g in main for m in g['meetings'] for s in ('us', 'them'))
say('drops from all other deaths or eaten later: us', du - u, 'them', dt - t, 'share', round((du - u) / (du - u + dt - t), 4))
# expected share if drop pearls went in proportion to living dragons at the meeting
exp = 0.0
n = 0
bal = [0, 0]
out_us = [0, 0]
out_them = [0, 0]
for g in main:
    for m in g['meetings']:
        w = sum(m['w15'][s]['us'] + m['w15'][s]['them'] for s in ('us', 'them'))
        wu = sum(m['w15'][s]['us'] for s in ('us', 'them'))
        a, b = m['alive_us'], m['alive_them']
        exp += w * a / (a + b)
        n += w
        r = a / b
        z = bal if 0.8 <= r <= 1.25 else out_us if r > 1.25 else out_them
        z[0] += wu
        z[1] += w - wu
say('share expected if pearls split like living dragons at the meeting:', round(exp / n, 4), 'observed', round(u / (u + t), 4))
say('meetings with dragon counts within 0.8-1.25: us', bal[0], 'them', bal[1], 'share', round(bal[0] / sum(bal), 4), '| we outnumber >1.25: ', out_us, round(out_us[0] / sum(out_us), 4), '| they outnumber:', out_them, round(out_them[0] / sum(out_them), 4))
for lab, lo, hi in (('r0-100', 0, 100), ('r101-300', 101, 300), ('r301+', 301, 999)):
    uu, t2, d2 = credit(main, pred=lambda m: lo <= m['round'] <= hi)
    say('meeting round', lab, 'us', uu, 'them', t2, 'share', round(uu / (uu + t2), 4))
say('by result: won', credit([g for g in main if g['win']]), round(share([g for g in main if g['win']]), 4), 'games', sum(g['win'] for g in main), '| lost', credit([g for g in main if not g['win']]), round(share([g for g in main if not g['win']]), 4), 'games', sum(not g['win'] for g in main))
say('by layout: games us them share | games fewer/more')
for k, gs in sorted(group(main, 'map_key').items()):
    uu, t2, d2 = credit(gs)
    say('  ', k, len(gs), uu, t2, round(uu / (uu + t2), 3) if uu + t2 else None, '|', sum(1 for g in gs if credit([g])[0] < credit([g])[1]), sum(1 for g in gs if credit([g])[0] > credit([g])[1]))
say('by opponent: games us them share')
for k, gs in sorted(group(main, 'opp').items(), key=lambda kv: -len(kv[1])):
    uu, t2, d2 = credit(gs)
    say('  ', k, sorted(set(g['band'] for g in gs)), len(gs), uu, t2, round(uu / (uu + t2), 3) if uu + t2 else None)
say('by bot id:', {k: (len(gs), credit(gs)[:2], round(share(gs), 3)) for k, gs in sorted(group(main, 'bot').items())})
for key in ('map_key', 'opp'):
    rs = []
    for k in sorted(set(g[key] for g in main)):
        rest = [g for g in main if g[key] != k]
        rs.append((round(share(rest), 4), k))
    rs.sort()
    say('leave one', key, 'out: lowest share', rs[0], 'highest', rs[-1])
for name, gs in (('ALL', main), ('1700-1899', [g for g in main if g['band'] == '1700-1899']), ('1900-2099', [g for g in main if g['band'] == '1900-2099']), ('first', [g for g in main if g['half'] == 'first']), ('second', [g for g in main if g['half'] == 'second'])):
    top = sorted(gs, key=lambda g: credit([g])[0] - credit([g])[1])[:3]
    ids = set(g['game'] for g in top)
    rest = [g for g in gs if g['game'] not in ids]
    say('  ', name, 'without its three most supporting games', [(g['game'], g['map_key'], credit([g])[:2]) for g in top], '->', credit(rest)[:2], round(share(rest), 4))
    rs = []
    for k in sorted(set(g['map_key'] for g in gs)):
        r2 = [g for g in gs if g['map_key'] != k]
        rs.append((round(share(r2), 4), k))
    rs.sort()
    say('     leave one layout out within slice: lowest', rs[0], 'highest', rs[-1])
    ps = sorted(share([g]) for g in gs if share([g]) is not None)
    say('     per-game share: median', round(median(ps), 3), 'games fewer/more/equal', sum(1 for g in gs if credit([g])[0] < credit([g])[1]), sum(1 for g in gs if credit([g])[0] > credit([g])[1]), sum(1 for g in gs if credit([g])[0] == credit([g])[1]))
# band 1700-1899 by opponent and layout
b1 = [g for g in main if g['band'] == '1700-1899']
say('band 1700-1899 by layout:', {k: (len(gs), credit(gs)[:2], round(share(gs), 3) if share(gs) is not None else None) for k, gs in sorted(group(b1, 'map_key').items())})
# layout-standardised comparison of the two bands: same layouts weighted the same
b2 = [g for g in main if g['band'] == '1900-2099']
l1 = group(b1, 'map_key')
l2 = group(b2, 'map_key')
say('per layout share, 1700-1899 vs 1900-2099:', {k: (round(share(l1[k]), 3) if k in l1 and share(l1[k]) is not None else None, round(share(l2[k]), 3) if k in l2 and share(l2[k]) is not None else None) for k in sorted(set(l1) | set(l2))})
Path(P + 'f2-numbers.txt').write_text('\n'.join(OUT) + '\n')

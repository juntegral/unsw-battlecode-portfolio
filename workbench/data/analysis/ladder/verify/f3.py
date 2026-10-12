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

maps = json.loads(Path('data/analysis/ladder/maps.json').read_text())
flagged = sorted(k for k, v in maps.items() if v.get('queen_spawn_dead_end'))
say('maps.json dead-end layouts', flagged, '| my layout keys missing from maps.json', sorted(set(g['map_key'] for g in games) - set(maps)))
say('main games', len(main), 'battle time span KST', min(g['at_kst'] for g in main), max(g['at_kst'] for g in main), 'battles', len(set(g['battle'] for g in main)))
EXCL = set(flagged)
keep = [g for g in main if g['map_key'] not in EXCL]
NAMES = {0: 'wall', 1: 'own body', 2: 'other body', 3: 'head-on', 4: 'no action'}


def q(g, s, reasons=(0, 1)):
    d = g['queen_death'][s]
    return d is not None and d['reason'] in reasons


def tally(gs):
    return dict(games=len(gs), ours=sum(q(g, 'us') for g in gs), ours_wall=sum(q(g, 'us', (0,)) for g in gs), ours_own=sum(q(g, 'us', (1,)) for g in gs),
                theirs=sum(q(g, 'them') for g in gs), theirs_wall=sum(q(g, 'them', (0,)) for g in gs), theirs_own=sum(q(g, 'them', (1,)) for g in gs))


say('ALL kept', tally(keep))
for b in ('<1700', '1700-1899', '1900-2099', '2100+'):
    say('band', b, tally([g for g in keep if g['band'] == b]))
for h in ('first', 'second'):
    say('half', h, 'main games in half', sum(1 for g in main if g['half'] == h), tally([g for g in keep if g['half'] == h]))
say('excluded layouts', tally([g for g in main if g['map_key'] in EXCL]), 'all 195', tally(main))
only_us = sum(1 for g in keep if q(g, 'us') and not q(g, 'them'))
only_them = sum(1 for g in keep if q(g, 'them') and not q(g, 'us'))
both = sum(1 for g in keep if q(g, 'them') and q(g, 'us'))
say('games: only ours', only_us, 'only theirs', only_them, 'both', both, 'neither', len(keep) - only_us - only_them - both, 'sign test two-sided p', round(sign(only_us, only_us + only_them), 4))


def ratio(gs):
    t = sum(q(g, 'them') for g in gs)
    return sum(q(g, 'us') for g in gs) / t if t else None


def diff(gs):
    return sum(q(g, 'us') for g in gs) - sum(q(g, 'them') for g in gs)


say('battle bootstrap 95% (2000 draws): ratio ours/theirs', boot(keep, ratio), 'difference ours-theirs in games', boot(keep, diff))
for name, gs in (('1700-1899', [g for g in keep if g['band'] == '1700-1899']), ('1900-2099', [g for g in keep if g['band'] == '1900-2099']), ('first', [g for g in keep if g['half'] == 'first']), ('second', [g for g in keep if g['half'] == 'second'])):
    ou = sum(1 for g in gs if q(g, 'us') and not q(g, 'them'))
    ot = sum(1 for g in gs if q(g, 'them') and not q(g, 'us'))
    say('  slice', name, 'ratio', ratio(gs), 'boot ratio', boot(gs, ratio), 'boot diff', boot(gs, diff), 'only ours/only theirs', ou, ot, 'sign p', round(sign(ou, ou + ot), 4))
say('queen fate, kept games (ours | theirs):')
for s in ('us', 'them'):
    c = Counter(NAMES[g['queen_death'][s]['reason']] if g['queen_death'][s] else 'alive at end' for g in keep)
    say('  ', s, dict(c), 'died any cause', len(keep) - c['alive at end'])
for s in ('us', 'them'):
    ds = [g['queen_death'][s] for g in keep if q(g, s)]
    say('  wall/own-body death of', s, 'queen: round median', median(d['round'] for d in ds), 'r0-100', sum(1 for d in ds if d['round'] <= 100), 'r101-300', sum(1 for d in ds if 100 < d['round'] <= 300), 'r301+', sum(1 for d in ds if d['round'] > 300), 'length median', median(d['length'] for d in ds), 'rounds', sorted(d['round'] for d in ds))
say('share of a side\'s queen deaths that are wall/own body: ours', sum(q(g, 'us') for g in keep), '/', sum(1 for g in keep if g['queen_death']['us']), 'theirs', sum(q(g, 'them') for g in keep), '/', sum(1 for g in keep if g['queen_death']['them']))
say('result: ours wall/own in games we won', sum(1 for g in keep if q(g, 'us') and g['win']), 'lost', sum(1 for g in keep if q(g, 'us') and not g['win']), '| theirs in games we won', sum(1 for g in keep if q(g, 'them') and g['win']), 'lost', sum(1 for g in keep if q(g, 'them') and not g['win']), '| kept games won', sum(g['win'] for g in keep), 'of', len(keep))
say('by layout: games ours theirs')
for k, gs in sorted(group(keep, 'map_key').items()):
    say('  ', k, len(gs), sum(q(g, 'us') for g in gs), sum(q(g, 'them') for g in gs))
say('by opponent: games ours theirs')
for k, gs in sorted(group(keep, 'opp').items(), key=lambda kv: -len(kv[1])):
    say('  ', k, len(gs), sum(q(g, 'us') for g in gs), sum(q(g, 'them') for g in gs))
say('by bot id:', {k: (len(gs), sum(q(g, 'us') for g in gs), sum(q(g, 'them') for g in gs)) for k, gs in sorted(group(keep, 'bot').items())})
say('by evening:', {k: (len(gs), sum(q(g, 'us') for g in gs), sum(q(g, 'them') for g in gs)) for k, gs in sorted(group(keep, 'evening').items())})
for key in ('map_key', 'opp'):
    rs = []
    for k in sorted(set(g[key] for g in keep)):
        rest = [g for g in keep if g[key] != k]
        rs.append((round(ratio(rest), 2), sum(q(g, 'us') for g in rest), sum(q(g, 'them') for g in rest), k))
    rs.sort()
    say('leave one', key, 'out: lowest ratio', rs[0], 'highest', rs[-1])
# two-start layouts versus the rest
two = [g for g in keep if g['start']['us'] == 2]
rest = [g for g in keep if g['start']['us'] != 2]
say('2-start layouts', tally(two), '| other kept layouts', tally(rest))
# remove the three layouts that support it most
sup = sorted(group(keep, 'map_key').items(), key=lambda kv: -(sum(q(g, 'us') for g in kv[1]) - sum(q(g, 'them') for g in kv[1])))[:3]
names = [k for k, v in sup]
rest = [g for g in keep if g['map_key'] not in names]
say('without the three most supporting layouts', names, tally(rest))
# hour blocks of the evening
say('by KST hour of battle:', {k: (len(gs), sum(q(g, 'us') for g in gs), sum(q(g, 'them') for g in gs)) for k, gs in sorted(group([dict(g, hour=g['at_kst'][5:13]) for g in keep], 'hour').items())})
Path(P + 'f3-numbers.txt').write_text('\n'.join(OUT) + '\n')

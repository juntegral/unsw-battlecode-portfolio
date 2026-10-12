# Own count for F7 (analyst, run 20261007-0208): what both sides do in raw rounds 0-100 of main games
# on the four 2-dragon-start layouts where stalls happen. Reads raw replays with the shared parser's loader.
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, Counter
from statistics import median
from pathlib import Path

D = Path('data/analysis/ladder')
rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
LAYOUTS = ('Tower Defense #1', 'Queen Of Spades #1', 'Trophy #1', 'Trauma #1')
REASON = ('wall', 'own body', 'other body', 'head-on', 'other')


def study(battle, game, upto=100):
    folder = Path('data/online/ladder') / str(battle)
    j = json.loads((folder / ('game-%d.json' % game)).read_text())
    root = replay.load(folder / ('M%d.replay' % game)).root()
    text = root.text(0)
    W, H = map(int, text.splitlines()[0].split()[1:3])
    bodies = {}
    teams = {}
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
    ours = 'A' if j['teamAId'] == 1119 else 'B'

    def side(i):
        return 'us' if teams[i] == ours else 'them'

    def md(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return min(dx, W - dx) + min(dy, H - dy)

    queens = dict((s, min(i for i in bodies if side(i) == s)) for s in ('us', 'them'))
    S = dict((s, dict(moves50=0, moves100=0, eats50=0, eats100=0, visited50=set(), first_eat=None, first_split=None, splits=0,
                      deaths=[], dist=[], alive={}, start=sorted(len(b) for i, b in bodies.items() if side(i) == s),
                      qvisited50=set(), qmoves50=0, qeats100=0, qsplits=0)) for s in ('us', 'them'))
    present = set()
    pearl_counts = []
    natural = 0
    rnd = 0
    actor = None
    started = False
    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart':
            if started:
                for s in ('us', 'them'):
                    heads = [b[0] for i, b in bodies.items() if side(i) == s]
                    S[s]['alive'][rnd] = len(heads)
                    if rnd <= 50 and heads and present:
                        S[s]['dist'].append(min(md(h, c) for h in heads for c in present))
                if rnd <= 50:
                    pearl_counts.append(len(present))
            started = True
            rnd = p.i32(0)
            actor = None
            if rnd > upto:
                break
        elif k == 'turnStart':
            actor = p.i32(0)
        elif k == 'tileChange':
            c = replay.point(p.pointer(0))
            if p.u32(0):
                present.add(c)
                if actor is None:
                    natural += 1
            else:
                present.discard(c)
                s = side(actor)
                S[s]['eats50' if rnd <= 50 else 'eats100'] += 1
                if actor == queens[s]:
                    S[s]['qeats100'] += 1
                if S[s]['first_eat'] is None:
                    S[s]['first_eat'] = rnd
        elif k == 'dragonUpdate':
            i = p.i32(0)
            h = replay.point(p.pointer(0))
            tail = replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != h:
                b.appendleft(h)
                s = side(i)
                S[s]['moves50' if rnd <= 50 else 'moves100'] += 1
                if rnd <= 50:
                    S[s]['visited50'].add(h)
                    if i == queens[s]:
                        S[s]['qvisited50'].add(h)
                        S[s]['qmoves50'] += 1
            while len(b) > 1 and b[-1] != tail:
                b.pop()
        elif k == 'dragonSplit':
            a = p.i32(0)
            s = side(a)
            for z, i in enumerate((a, p.i32(4))):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            S[s]['splits'] += 1
            if a == queens[s]:
                S[s]['qsplits'] += 1
            if S[s]['first_split'] is None:
                S[s]['first_split'] = rnd
        elif k == 'dragonDeath':
            i = p.i32(0)
            S[side(i)]['deaths'].append((rnd, REASON[p.u16(4)], len(bodies[i]), 'queen' if i == queens[side(i)] else 'other'))
            bodies.pop(i)
    out = dict(W=W, H=H, natural=natural, pearls_on_board_median=median(pearl_counts) if pearl_counts else None)
    for s in ('us', 'them'):
        x = S[s]
        out[s] = dict(start=x['start'], moves50=x['moves50'], visited50=len(x['visited50']), novelty=round(len(x['visited50']) / max(1, x['moves50']), 2),
                      eats50=x['eats50'], eats100=x['eats50'] + x['eats100'], first_eat=x['first_eat'], first_split=x['first_split'], splits=x['splits'],
                      alive25=x['alive'].get(25), alive50=x['alive'].get(50), alive100=x['alive'].get(100),
                      dist_median=median(x['dist']) if x['dist'] else None, deaths=x['deaths'][:8], ndeaths=len(x['deaths']),
                      qnovelty=round(len(x['qvisited50']) / max(1, x['qmoves50']), 2), qmoves50=x['qmoves50'], qeats100=x['qeats100'], qsplits=x['qsplits'])
    return out


sel = [r for r in rows if r['our_code'] == 'main' and r['map_key'] in LAYOUTS and r['curves']['100']]
res = []
for r in sel:
    c = r['curves']['100']
    stall = c['us']['alive'] <= 6 and c['them']['alive'] >= 15
    o = study(r['battle'], r['game'])
    assert o['us']['alive100'] == c['us']['alive'] and o['them']['alive100'] == c['them']['alive'], (r['game'], o['us']['alive100'], c['us']['alive'])
    assert o['us']['eats100'] == r['pearls']['r0-100']['eaten']['us'] and o['them']['eats100'] == r['pearls']['r0-100']['eaten']['them'], r['game']
    res.append((r, stall, o))

print('games', len(res), 'stall', sum(s for _, s, _ in res), '(alive at r100 and pearls r0-100 match rows.jsonl in every game)')
print()
print('STALL GAMES, one line each: us | them')
for r, stall, o in res:
    if not stall:
        continue
    u = o['us']
    t = o['them']
    print(r['battle'], r['game'], r['map_key'], r['opponent_rating'], 'win' if r['win'] else 'loss', 'natural births r0-100', o['natural'], 'on board median', o['pearls_on_board_median'])
    for nm, x in (('  us  ', u), ('  them', t)):
        print(nm, 'start', x['start'], 'moves50', x['moves50'], 'distinct50', x['visited50'], 'novelty', x['novelty'], 'eats50', x['eats50'], 'eats100', x['eats100'],
              'first eat', x['first_eat'], 'first split', x['first_split'], 'splits', x['splits'], 'alive 25/50/100', x['alive25'], x['alive50'], x['alive100'],
              'dist to pearl median', x['dist_median'], 'queen: novelty', x['qnovelty'], 'moves50', x['qmoves50'], 'eats', x['qeats100'], 'splits', x['qsplits'], 'deaths', x['ndeaths'], x['deaths'][:5])


def med(xs):
    xs = [x for x in xs if x is not None]
    return median(xs) if xs else None


print()
for label, flag in (('STALL', True), ('NON-STALL same layouts', False)):
    g = [(r, o) for r, s, o in res if s == flag]
    print(label, 'games', len(g), 'wins', sum(r['win'] for r, _ in g))
    for s in ('us', 'them'):
        print('  ', s, dict((key, med([o[s][key] for _, o in g])) for key in ('moves50', 'visited50', 'novelty', 'eats50', 'eats100', 'first_eat', 'first_split', 'splits', 'alive25', 'alive50', 'alive100', 'dist_median', 'qnovelty', 'qeats100', 'qsplits', 'ndeaths')),
              'never ate by r100:', sum(o[s]['first_eat'] is None for _, o in g), 'never split by r100:', sum(o[s]['first_split'] is None for _, o in g))
    ratio = [o['us']['novelty'] / o['them']['novelty'] for _, o in g if o['them']['novelty'] > 0]
    print('   our novelty / their novelty: median', round(median(ratio), 2), '| games with ratio >= 0.5:', sum(x >= 0.5 for x in ratio), 'of', len(ratio))
    print('   natural births r0-100 median', med([o['natural'] for _, o in g]), '| pearls on board median', med([o['pearls_on_board_median'] for _, o in g]))
    print('   our first death by r50: games', sum(1 for _, o in g if any(d[0] <= 50 for d in o['us']['deaths'])), '| our deaths r0-50 causes', dict(Counter(d[1] for _, o in g for d in o['us']['deaths'] if d[0] <= 50)))


print()
print('PER LAYOUT, stall / non-stall medians (us | them)')
KEYS = ('moves50', 'visited50', 'novelty', 'eats50', 'eats100', 'first_eat', 'first_split', 'splits', 'alive50', 'alive100', 'dist_median', 'ndeaths')
for lay in LAYOUTS:
    for label, flag in (('stall', True), ('non-stall', False)):
        g = [(r, o) for r, s, o in res if s == flag and r['map_key'] == lay]
        if not g:
            continue
        print(lay, label, 'games', len(g), 'wins', sum(r['win'] for r, _ in g), 'opp rating median', med([r['opponent_rating'] for r, _ in g]))
        for s in ('us', 'them'):
            print('    ', s, dict((key, med([o[s][key] for _, o in g])) for key in KEYS))
print()
print('pearls eaten by r50, all 53 games: us<=2:', sum(o['us']['eats50'] <= 2 for _, _, o in res), 'them<=2:', sum(o['them']['eats50'] <= 2 for _, _, o in res))
low = [(r, s, o) for r, s, o in res if o['us']['eats50'] <= 2]
print('when we ate <=2 by r50: games', len(low), 'stall', sum(s for _, s, _ in low), 'wins', sum(r['win'] for r, _, _ in low))
low = [(r, s, o) for r, s, o in res if o['them']['eats50'] <= 2]
print('when they ate <=2 by r50: games', len(low), 'our wins', sum(r['win'] for r, _, _ in low), 'their alive at r100 median', med([o['them']['alive100'] for _, _, o in low]))
late = [(r, s, o) for r, s, o in res if o['us']['first_split'] is None or o['us']['first_split'] > 40]
print('our first split after r40 (or none): games', len(late), 'stall', sum(s for _, s, _ in late), 'wins', sum(r['win'] for r, _, _ in late))
late = [(r, s, o) for r, s, o in res if o['them']['first_split'] is None or o['them']['first_split'] > 40]
print('their first split after r40 (or none): games', len(late), 'our wins', sum(r['win'] for r, _, _ in late), 'their alive at r100 median', med([o['them']['alive100'] for _, _, o in late]))
print('pearls eaten in r51-100, games where a side had <=3 alive at r50: us', med([o['us']['eats100'] - o['us']['eats50'] for _, _, o in res if o['us']['alive50'] <= 3]), 'n', sum(o['us']['alive50'] <= 3 for _, _, o in res),
      '| them', med([o['them']['eats100'] - o['them']['eats50'] for _, _, o in res if o['them']['alive50'] <= 3]), 'n', sum(o['them']['alive50'] <= 3 for _, _, o in res))
print('splits in r0-100, same condition: us', med([o['us']['splits'] for _, _, o in res if o['us']['alive50'] <= 3]), '| them', med([o['them']['splits'] for _, _, o in res if o['them']['alive50'] <= 3]))

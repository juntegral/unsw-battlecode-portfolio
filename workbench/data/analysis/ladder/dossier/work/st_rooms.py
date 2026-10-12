# Scratch (diag-stripes): pearls by room class, room visits and their outcome, and the decision at a portal mouth.
# Usage: python3 data/analysis/ladder/dossier/work/st_rooms.py <rows file> [maxround]
import sys, json
from collections import Counter, defaultdict

MAXR = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 6
games = [json.loads(line) for line in open(sys.argv[1])]


def cls(size, loop):
    if size >= 48:
        return 'main'
    return ('loop%d' if loop else 'dead%d') % size


def lb(L):
    return '2' if L <= 2 else '3' if L == 3 else '4-6' if L <= 6 else '7+'


print('games', len(games), 'won', sum(g['result'] == 'win' for g in games))
# 1. pearls
born = Counter()
eat = Counter()
for g in games:
    for c, b, o, by, er, eid, eL, eq in g['pearls']:
        k = cls(g['size'][g['comp'][c]], g['loop'][g['comp'][c]])
        if b <= MAXR:
            born[k, o] += 1
        if by is not None and er <= MAXR:
            eat[k, by] += 1
            eat[k, by, 'q' if eq else 'o'] += 1
            for lim in (50, 100):
                if er <= lim:
                    eat[k, by, lim] += 1
print()
print('1. pearls by where the tile is (class = size of the kelp-closed room; loop = a portal edge lies inside the room)')
print('class     born natural / dropped | eaten ours (queen) / theirs (queen) | by r50 ours/theirs | by r100 ours/theirs')
for k in ('main', 'loop4', 'dead4', 'dead3', 'dead1'):
    print('%-8s %6d / %4d | %5d (%4d) / %5d (%4d) | %4d / %4d | %4d / %4d' % (
        k, born[k, 'n'], born[k, 'd'], eat[k, 'u'], eat[k, 'u', 'q'], eat[k, 't'], eat[k, 't', 'q'],
        eat[k, 'u', 50], eat[k, 't', 50], eat[k, 'u', 100], eat[k, 't', 100]))

# 2. visits
visits = []
for g in games:
    comp, size, loop = g['comp'], g['size'], g['loop']
    where = {}
    openv = {}
    for t in g['turns']:
        if t['r'] > MAXR:
            break
        i = t['id']
        if i not in where:
            where[i] = comp[t['head']]
            if size[where[i]] < 48 and i not in openv:
                # born inside (split child) or started inside
                openv[i] = dict(game=g['game'], s=t['s'], id=i, q=t['q'], r=t['r'], L=t['L'], k=cls(size[where[i]], loop[where[i]]),
                                born=1, pe=0, pr=0, ate=0, splits=0, out=None, turns=0, kids_out=0, others=0, res=g['result'])
        v = openv.get(i)
        if v is not None:
            v['turns'] += 1
        pos = t['head']
        for n, c in enumerate(t['steps']):
            cp = comp[c]
            if cp != where[i]:
                if v is not None:
                    v['out'] = 'left'
                    v['rout'] = t['r']
                    v['Lout'] = t['L'] + t['ate']
                    visits.append(v)
                    v = None
                    openv.pop(i)
                if size[cp] < 48:
                    d = t['dirs'][n][0]
                    o = t['opts'][d] if n == 0 else None
                    v = dict(game=g['game'], s=t['s'], id=i, q=t['q'], r=t['r'], L=t['L'], k=cls(size[cp], loop[cp]), born=0,
                             pe=o[4] if o else -1, pr=o[5] if o else -1, others=o[7] if o else -1,
                             ate=0, splits=0, out=None, turns=1, kids_out=0, res=g['result'])
                    openv[i] = v
                where[i] = cp
            pos = c
        if v is not None:
            # pearls eaten this turn while the head ends in the room: count all pearls of the turn after entry
            v['ate'] += t['ate']
            if t['split'] is not None:
                v['splits'] += 1
                kid_head = t['split'][1][0]
                v['kids_out'] += size[comp[kid_head]] >= 48
            if t['died'] is not None:
                v['out'] = t['died']
                v['rout'] = t['r']
                visits.append(v)
                openv.pop(i)
        if t['died'] is not None:
            where.pop(i, None)
            openv.pop(i, None)
    for v in openv.values():
        if v['out'] is None:
            v['out'] = 'open at end'
            visits.append(v)
print()
print('2. visits to a small room (entered through a portal, or a child born inside)')
print('class side  visits (queen) per game | pearls eaten inside per visit | left alive | died inside: wall, own body, other body, head-on, no action | splits inside (child head outside) | killed by others inside / open at end')
for k in ('loop4', 'dead3', 'dead1'):
    for s in 'ut':
        vs = [v for v in visits if v['k'] == k and v['s'] == s]
        if not vs:
            print('%-6s %s  0' % (k, s))
            continue
        c = Counter(v['out'] for v in vs)
        print('%-6s %s  %4d (%3d) %5.1f | %5.2f | %4d (%.2f) | %d, %d, %d, %d, %d | %d (%d) | %d' % (
            k, 'ours' if s == 'u' else 'thrs', len(vs), sum(v['q'] for v in vs), len(vs) / len(games),
            sum(v['ate'] for v in vs) / len(vs), c['left'], c['left'] / len(vs),
            c['wall'], c['own body'], c['other body'], c['head-on'], c['no action'],
            sum(v['splits'] for v in vs), sum(v['kids_out'] for v in vs), c['open at end']))
print()
print('   entry length of the visitor, loop4 and dead3: class side | L2 L3 L4-6 L7+ : visits, left alive, pearls eaten')
for k in ('loop4', 'dead3', 'dead1'):
    for s in 'ut':
        row = []
        for b in ('2', '3', '4-6', '7+'):
            vs = [v for v in visits if v['k'] == k and v['s'] == s and lb(v['L']) == b and not v['born']]
            row.append('%s: %d, %d, %d' % (b, len(vs), sum(v['out'] == 'left' for v in vs), sum(v['ate'] for v in vs)))
        print('  ', k, 'ours' if s == 'u' else 'thrs', '|', ' | '.join(row))
print()
print('   net length for the side from one visit (pearls eaten inside minus the length that died inside; drops not credited):')
for k in ('loop4', 'dead3', 'dead1'):
    for s in 'ut':
        vs = [v for v in visits if v['k'] == k and v['s'] == s]
        print('  ', k, 'ours' if s == 'u' else 'thrs', 'visits', len(vs), 'pearls', sum(v['ate'] for v in vs),
              'visits ending in death', sum(v['out'] not in ('left', 'open at end') for v in vs))

# 3. the decision at a mouth
dec = Counter()
for g in games:
    for t in g['turns']:
        if t['r'] > MAXR:
            break
        if t['hs'] < 48:
            continue
        first = t['steps'][0] if t['steps'] else None
        fd = t['dirs'][0][0] if t['dirs'] else None
        for d, o in enumerate(t['opts']):
            if o is None or o[0] != 2 or o[2] >= 48:
                continue
            if o[6] != 0:
                continue
            k = cls(o[2], o[3])
            took = int(fd == d)
            pe = 'pearl on entry tile' if o[4] else ('pearl deeper only' if o[5] > 0 else 'no pearl in room')
            dec[k, t['s'], 'q' if t['q'] else 'o', lb(t['L']), pe, took] += 1
            dec[k, t['s'], 'q' if t['q'] else 'o', 'all', pe, took] += 1
            dec[k, t['s'], 'q' if t['q'] else 'o', 'all', 'any', took] += 1
print()
print('3. turns that start on a main-area tile with a free portal step into a small room: took it / chances')
for k in ('loop4', 'dead3', 'dead1'):
    for pe in ('any', 'pearl on entry tile', 'pearl deeper only', 'no pearl in room'):
        for who in ('o', 'q'):
            for b in ('all', '2', '3', '4-6', '7+'):
                if pe == 'any' and b != 'all':
                    continue
                u1, u0 = dec[k, 'u', who, b, pe, 1], dec[k, 'u', who, b, pe, 0]
                t1, t0 = dec[k, 't', who, b, pe, 1], dec[k, 't', who, b, pe, 0]
                if u1 + u0 + t1 + t0 == 0:
                    continue
                print('  %-6s %-20s %-6s L %-4s ours %4d / %4d (%s)   theirs %4d / %4d (%s)' % (
                    k, pe, 'queen' if who == 'q' else 'other', b, u1, u1 + u0, '%.2f' % (u1 / (u1 + u0)) if u1 + u0 else '-',
                    t1, t1 + t0, '%.2f' % (t1 / (t1 + t0)) if t1 + t0 else '-'))
json.dump(visits, open('~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/dossier/work/st_visits.json', 'w'))

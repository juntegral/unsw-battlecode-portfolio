# Own count (analyst, run 20261007-0500): the queens on one layout (default Portals #1), main and v31 games.
# Room = tiles joined by open edges (kelp and portal edges closed). For each queen: death round, cause, length, room size at death,
# side of the body she hit, portal steps before death, share of her turns spent in a room of 6 tiles or fewer, room size at r50 and r100.
# Usage: python3 data/analysis/ladder/work/h9_portalq.py [map_key]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict, Counter
from statistics import median
from pathlib import Path

D = Path('data/analysis/ladder')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
CAUSE = ('wall', 'own body', 'other body', 'head-on', 'other')


def build(W, H, raw):
    edges = canonical_edges(W, H, raw)
    portals = defaultdict(list)
    for e, kp in edges.items():
        if kp[0] == 2:
            portals[kp[1]].append(e)
    plain = dict()
    pnx = dict()
    for y in range(H):
        for x in range(W):
            out = []
            pout = []
            for d in range(4):
                e = edge_id(W, H, x, y, d)
                kind, pid = edges.get(e, (0, -1))
                if kind == 1:
                    continue
                if kind == 2:
                    partner = [z for z in portals[pid] if z != e]
                    if len(partner) != 1:
                        continue
                    row, px = divmod(partner[0], W + 1)
                    pout.append(((px - (d == 3)) % W, (row // 2 - (d == 0)) % H))
                else:
                    out.append(((x + STEP[d][0]) % W, (y + STEP[d][1]) % H))
            plain[(x, y)] = out
            pnx[(x, y)] = pout
    room = dict()
    for c in plain:
        if c in room:
            continue
        seen = set([c])
        frontier = [c]
        while frontier:
            new = []
            for a in frontier:
                for t in plain[a]:
                    if t not in seen:
                        seen.add(t)
                        new.append(t)
            frontier = new
        for a in seen:
            room[a] = len(seen)
    return plain, pnx, room


def study(r):
    battle, game = r['battle'], r['game']
    folder = Path('data/online/ladder') / str(battle)
    j = json.loads((folder / ('game-%d.json' % game)).read_text())
    root = replay.load(folder / ('M%d.replay' % game)).root()
    text = root.text(0)
    W, H = map(int, text.splitlines()[0].split()[1:3])
    bodies = dict()
    teams = dict()
    raw = []
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int, q[1:4])))
    ours = 'A' if j['teamAId'] == 1119 else 'B'

    def side(i):
        return 'us' if teams[i] == ours else 'them'

    plain, pnx, room = build(W, H, raw)
    queens = dict((s, min(i for i in bodies if side(i) == s)) for s in ('us', 'them'))
    qside = dict((v, k) for k, v in queens.items())
    out = dict((s, dict(turns=0, small=0, psteps=0, death=None, r50=None, r100=None, spawn_room=room[bodies[queens[s]][0]], splits=0, first_small=None)) for s in ('us', 'them'))
    rnd = 0
    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart':
            rnd = p.i32(0)
            if rnd in (50, 100):
                for s in ('us', 'them'):
                    if queens[s] in bodies:
                        out[s]['r%d' % rnd] = room[bodies[queens[s]][0]]
        elif k == 'turnStart':
            a = p.i32(0)
            if a in qside and a in bodies:
                o = out[qside[a]]
                o['turns'] += 1
                if room[bodies[a][0]] <= 6:
                    o['small'] += 1
                    if o['first_small'] is None:
                        o['first_small'] = rnd
        elif k == 'dragonUpdate':
            i = p.i32(0)
            h = replay.point(p.pointer(0))
            tail = replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != h:
                if i in qside and h in pnx[b[0]] and h not in plain[b[0]]:
                    out[qside[i]]['psteps'] += 1
                b.appendleft(h)
            while len(b) > 1 and b[-1] != tail:
                b.pop()
        elif k == 'dragonSplit':
            par = p.i32(0)
            if par in qside:
                out[qside[par]]['splits'] += 1
            for z, i in enumerate((par, p.i32(4))):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 'dragonDeath':
            i = p.i32(0)
            if i in qside:
                s = qside[i]
                h = bodies[i][0]
                hit = r['queen']['us' if s == 'us' else 'them'].get('death_hit_id')
                mates = sum(1 for z, bb in bodies.items() if z != i and side(z) == s and room[bb[0]] == room[h] and any(c == h or c in plain[h] for c in bb))
                out[s]['death'] = dict(round=rnd, cause=CAUSE[p.u16(4)], length=len(bodies[i]), room=room[h], hit_side=(side(hit) if hit in teams else None) if hit is not None else None, own_bodies_touching=mates)
            bodies.pop(i)
    return out


def main():
    key = sys.argv[1] if len(sys.argv) > 1 else 'Portals #1'
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    for code in ('main', 'v31'):
        sel = [r for r in rows if r['our_code'] == code and r['map_key'] == key]
        res = []
        for r in sel:
            o = study(r)
            res.append((r, o))
            du = o['us']['death']
            dt = o['them']['death']
            print(code, r['battle'], r['game'], 'win' if r['win'] else 'loss', r['opponent_rating'],
                  '| ours', (du['round'], du['cause'], du['length'], 'room', du['room'], 'hit', du['hit_side']) if du else 'alive', 'psteps', o['us']['psteps'], 'small turns %d/%d' % (o['us']['small'], o['us']['turns']), 'first small', o['us']['first_small'], 'splits', o['us']['splits'],
                  '| theirs', (dt['round'], dt['cause'], dt['length'], 'room', dt['room'], 'hit', dt['hit_side']) if dt else 'alive', 'psteps', o['them']['psteps'], 'small turns %d/%d' % (o['them']['small'], o['them']['turns']), 'splits', o['them']['splits'])
        for s in ('us', 'them'):
            dead = [o[s]['death'] for r, o in res if o[s]['death']]
            print('  ', code, s, 'games', len(res), 'queen died', len(dead), 'in a room of 6 or fewer', sum(1 for d in dead if d['room'] <= 6), 'room sizes', dict(Counter(d['room'] for d in dead)),
                  'causes', dict(Counter(d['cause'] for d in dead)), 'hit side', dict(Counter(str(d['hit_side']) for d in dead if d['cause'] == 'other body')),
                  'median portal steps', median([o[s]['psteps'] for r, o in res]), 'queens with a portal step', sum(1 for r, o in res if o[s]['psteps'] > 0),
                  'turns in small rooms', sum(o[s]['small'] for r, o in res), 'of', sum(o[s]['turns'] for r, o in res),
                  'room at r50', dict(Counter(str(o[s]['r50']) for r, o in res)), 'spawn room', dict(Counter(o[s]['spawn_room'] for r, o in res)), 'median splits', median([o[s]['splits'] for r, o in res]))


main()

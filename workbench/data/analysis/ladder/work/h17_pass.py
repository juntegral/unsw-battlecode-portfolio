# Own count (analyst, run 20261007-0800), bar F37_board. One JSON line per game in which a queen died by wall or own body in raw rounds 101-200
# (free layouts, main or v31). deaths: per such queen death: side, round, reason (0 wall, 1 own body), queen length at the start of her last turn,
#   cats: what is on each of the four tiles next to her head at the start of that turn, in the order north, east, south, west:
#     kelp (blocked edge), self (her own body), child (a living dragon born from one of her splits), ally (another dragon of her team), enemy, free;
#   a portal edge is followed to its exit tile. splits10: queen splits in the 10 rounds up to the death; last_split: round of her latest split.
# Usage: python3 data/analysis/ladder/work/h17_pass.py
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict
from pathlib import Path

P = '~/01. Project/개인 프로젝트/unsw-swarm/data/analysis/ladder/work/'
D = Path('data/analysis/ladder')
STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))


def build_dir(W, H, raw):
    edges = canonical_edges(W, H, raw)
    portals = defaultdict(list)
    for e, kp in edges.items():
        if kp[0] == 2:
            portals[kp[1]].append(e)
    dn = dict()
    for y in range(H):
        for x in range(W):
            out = []
            for d in range(4):
                e = edge_id(W, H, x, y, d)
                kind, pid = edges.get(e, (0, -1))
                if kind == 1:
                    out.append(None)
                elif kind == 2:
                    partner = [z for z in portals[pid] if z != e]
                    if len(partner) != 1:
                        out.append(None)
                        continue
                    row, px = divmod(partner[0], W + 1)
                    out.append(((px - (d == 3)) % W, (row // 2 - (d == 0)) % H))
                else:
                    out.append(((x + STEP[d][0]) % W, (y + STEP[d][1]) % H))
            dn[(x, y)] = out
    return dn


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

    queens = dict((s, min(i for i in bodies if side(i) == s)) for s in ('us', 'them'))
    qids = (queens['us'], queens['them'])
    dn = build_dir(W, H, raw)
    qsplits = dict(us=[], them=[])
    children = dict(us=set(), them=set())
    snap = dict()
    qdead = dict()
    deaths = []
    rnd = 0
    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart':
            rnd = p.i32(0)
        elif k == 'turnStart':
            actor = p.i32(0)
            if actor in qids and actor in bodies:
                occ = dict()
                for z, bb in bodies.items():
                    for c in bb:
                        occ[c] = z
                snap[side(actor)] = (rnd, bodies[actor][0], occ, len(bodies[actor]))
        elif k == 'dragonUpdate':
            i = p.i32(0)
            h = replay.point(p.pointer(0))
            tail = replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != h:
                b.appendleft(h)
            while len(b) > 1 and b[-1] != tail:
                b.pop()
        elif k == 'dragonSplit':
            a, c2 = p.i32(0), p.i32(4)
            for z, i in enumerate((a, c2)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            if a in qids:
                qsplits[side(a)].append(rnd)
                children[side(a)].add(c2)
            elif c2 in qids:
                qsplits[side(c2)].append(rnd)
                children[side(c2)].add(a)
        elif k == 'dragonDeath':
            i = p.i32(0)
            reason = p.u16(4)
            if i in qids:
                s = side(i)
                o = 'them' if s == 'us' else 'us'
                sn = snap.get(s)
                if reason in (0, 1) and sn is not None:
                    cats = []
                    for t in dn[sn[1]]:
                        if t is None:
                            cats.append('kelp')
                            continue
                        z = sn[2].get(t)
                        if z is None:
                            cats.append('free')
                        elif z == i:
                            cats.append('self')
                        elif z in children[s]:
                            cats.append('child')
                        elif z in teams and side(z) == s:
                            cats.append('ally')
                        else:
                            cats.append('enemy')
                    deaths.append(dict(side=s, round=rnd, reason=reason, qlen=sn[3], turn_round=sn[0], cats=cats,
                                       splits10=sum(1 for x in qsplits[s] if rnd - 10 <= x <= rnd),
                                       last_split=qsplits[s][-1] if qsplits[s] else None, nsplits=len(qsplits[s]),
                                       other_queen_dead=o in qdead))
                qdead[s] = rnd
            bodies.pop(i)
    return dict(game=game, battle=battle, deaths=deaths)


def main():
    rows = [json.loads(l) for l in (D / 'rows.jsonl').read_text().splitlines() if l.strip()]
    maps = json.loads((D / 'maps.json').read_text())
    sel = []
    for r in rows:
        if r['our_code'] not in ('main', 'v31') or maps[r['map_key']]['queen_spawn_dead_end']:
            continue
        for s in ('us', 'them'):
            q = r['queen'][s]
            if q['death_cause'] in ('wall', 'own body') and 101 <= q['death_round'] <= 200:
                sel.append(r)
                break
    out = open(P + 'h17.jsonl', 'w')
    done = 0
    for r in sel:
        try:
            rec = study(r)
        except Exception as e:
            rec = dict(game=r['game'], battle=r['battle'], error='%s: %s' % (type(e).__name__, e))
        out.write(json.dumps(rec) + '\n')
        out.flush()
        done += 1
    out.close()
    print('games written', done)


main()

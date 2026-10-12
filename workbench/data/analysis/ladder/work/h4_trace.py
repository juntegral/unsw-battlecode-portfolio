# Own look (analyst, run 20261007-0400): round-by-round trace of one game's opening, printed to the screen.
# Per round: pearls on the board, every dragon's head, length and path distance to the nearest pearl
# (kelp and portals respected; first number ignores dragons, second treats every body tile as blocked), then the round's meals, splits and deaths.
# Usage: python3 data/analysis/ladder/work/h4_trace.py <battle> <game> <first round> <last round>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay, edge_id, canonical_edges
from collections import deque, defaultdict
from pathlib import Path

STEP = ((0, -1), (1, 0), (0, 1), (-1, 0))
REASON = ('wall', 'own body', 'other body', 'head-on', 'no action')


def build_nxt(W, H, raw):
    edges = canonical_edges(W, H, raw)
    portals = defaultdict(list)
    for e, kp in edges.items():
        if kp[0] == 2:
            portals[kp[1]].append(e)
    nxt = dict()
    for y in range(H):
        for x in range(W):
            out = []
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
                    out.append(((px - (d == 3)) % W, (row // 2 - (d == 0)) % H))
                else:
                    out.append(((x + STEP[d][0]) % W, (y + STEP[d][1]) % H))
            nxt[(x, y)] = out
    return nxt


def near(nxt, src, pset, blocked):
    if not pset:
        return None
    seen = set([src])
    frontier = [src]
    d = 0
    while frontier and d < 60:
        d += 1
        new = []
        for c in frontier:
            for t in nxt[c]:
                if t in seen or t in blocked:
                    continue
                if t in pset:
                    return d
                seen.add(t)
                new.append(t)
        frontier = new
    return None


def main():
    battle, game, r0, r1 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
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
    nxt = build_nxt(W, H, raw)
    print('size', W, H, 'our side', ours)
    present = set()
    rnd = 0
    started = False
    actor = None
    evs = []

    def show():
        if rnd < r0 or rnd > r1:
            return
        blocked = set(c for bb in bodies.values() for c in bb)
        parts = []
        for s in ('us', 'them'):
            items = []
            for z, bb in sorted(bodies.items()):
                if (teams[z] == ours) != (s == 'us'):
                    continue
                items.append('%d@%d,%d L%d p%s/%s' % (z, bb[0][0], bb[0][1], len(bb), near(nxt, bb[0], present, set()), near(nxt, bb[0], present, blocked)))
            parts.append(s + ': ' + '; '.join(items[:8]) + (' (+%d more)' % (len(items) - 8) if len(items) > 8 else ''))
        print('r%d pearls %d | %s | %s | %s' % (rnd, len(present), parts[0], parts[1], ', '.join(evs)))

    for ev in root.pointer(3):
        k = replay.EVENT_NAMES[ev.u16(0)]
        p = ev.pointer(0)
        if k == 'roundStart':
            if started:
                show()
            started = True
            evs = []
            rnd = p.i32(0)
            if rnd > r1:
                break
            actor = None
        elif k == 'turnStart':
            actor = p.i32(0)
        elif k == 'tileChange':
            c = replay.point(p.pointer(0))
            if p.u32(0):
                present.add(c)
            else:
                present.discard(c)
                if actor in teams:
                    evs.append('%s %d eats %d,%d' % ('us' if teams[actor] == ours else 'them', actor, c[0], c[1]))
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
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            evs.append('%s %d splits off %d' % ('us' if teams[p.i32(0)] == ours else 'them', p.i32(0), p.i32(4)))
        elif k == 'dragonDeath':
            i = p.i32(0)
            evs.append('%s %d dies (%s) L%d' % ('us' if teams[i] == ours else 'them', i, REASON[p.u16(4)], len(bodies[i])))
            bodies.pop(i)
    show()


main()

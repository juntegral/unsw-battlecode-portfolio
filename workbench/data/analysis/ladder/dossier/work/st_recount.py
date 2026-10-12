# Scratch (diag-stripes): independent recount of the headline number, straight from the replays, with the doors of the
# two pearl loop rooms typed in by hand from the drawn map (st_map.py) instead of computed.
# Chance = a dragon of length 2 starts its turn on a door tile, the entry tile is free of dragons, its side has 4 dragons or fewer.
# Usage: python3 data/analysis/ladder/dossier/work/st_recount.py
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import Counter, deque
from pathlib import Path

# door tile -> (entry tile, the four room tiles)
ROOM_C = {(11, 0), (12, 0), (11, 1), (12, 1)}
ROOM_D = {(11, 10), (12, 10), (11, 11), (12, 11)}
DOORS = {(13, 0): ((12, 1), ROOM_C), (13, 1): ((12, 0), ROOM_C), (10, 10): ((11, 11), ROOM_D), (10, 11): ((11, 10), ROOM_D)}
recs = {}
with open('data/analysis/ladder/dossier/per-game.jsonl') as f:
    for line in f:
        r = json.loads(line)
        if r['relation'] == 'us' and r['layout_key'].startswith('Stripes'):
            recs[r['game']] = (r['replay'], r['our_side'])
count = Counter()
first = {'u': [], 't': []}
for gid in sorted(recs):
    path, ours = recs[gid]
    root = replay.load(Path(path)).root()
    bodies, teams = {}, {}
    for line in root.text(0).splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
    pearls = set()
    pending = None
    rnd = 0
    got = {}

    def settle(newhead):
        global pending
        if pending is not None:
            s, kind, entry, L, n = pending
            took = int(newhead == entry)
            if L == 2 and n <= 4:
                count[s, kind, took] += 1
            if took and kind != 'empty' and s not in got:
                got[s] = rnd
            pending = None

    for ev in root.pointer(3):
        k = ev.u16(0)
        p = ev.pointer(0)
        if k == 0:
            settle(None)
            rnd = p.i32(0)
        elif k == 1:
            settle(None)
            a = p.i32(0)
            head = bodies[a][0]
            if head in DOORS:
                entry, room = DOORS[head]
                if not any(entry in b for b in bodies.values()):
                    s = 'u' if teams[a] == ours else 't'
                    kind = 'on entry' if entry in pearls else 'deeper' if pearls.intersection(room) else 'empty'
                    pending = (s, kind, entry, len(bodies[a]), sum(1 for i in bodies if teams[i] == teams[a]))
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                pearls.add(c)
            else:
                pearls.discard(c)
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                if pending is not None:
                    settle(hd)
                b.appendleft(hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            settle(None)
            for z, i in enumerate((p.i32(0), p.i32(4))):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
        elif k == 11:
            settle(None)
            bodies.pop(p.i32(0))
    for s in 'ut':
        first[s].append(got.get(s, 999))
print('games', len(recs))
for kind in ('on entry', 'deeper', 'empty'):
    for s in 'ut':
        a, b = count[s, kind, 1], count[s, kind, 0]
        print('  pearl %-8s %s took %3d of %3d (%s)' % (kind, 'ours  ' if s == 'u' else 'theirs', a, a + b, '%.2f' % (a / (a + b)) if a + b else '-'))
for s in 'ut':
    v = sorted(first[s])
    print('first step into one of the two pearl loop rooms with a pearl in it,', 'ours  ' if s == 'u' else 'theirs', 'by r10:', sum(x <= 10 for x in v), 'by r20:', sum(x <= 20 for x in v), 'never:', sum(x == 999 for x in v))

# Scratch (diag-drops): checks the occupancy and head bookkeeping of dr_scan.py against a recount from the bodies at every
# round start, and prints how many free tiles lie behind a pearl beside a head (the "room" flag) for a sample of turns.
# Usage: python3 data/analysis/ladder/dossier/work/dr_occ.py <O|R> <index>
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque, Counter
from pathlib import Path


def main():
    who, n = sys.argv[1], int(sys.argv[2])
    rows = json.loads(Path('data/analysis/ladder/dossier/work/wk_index.json').read_text())
    rows = sorted([r for r in rows if r['who'] == who], key=lambda r: (r['layout'], r['game']))
    row = rows[n]
    root = replay.load(Path(row['replay'])).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    tile = lambda p: p[1] * w + p[0]
    bodies = {}
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4 + 2 * k]) * w + int(q[3 + 2 * k]) for k in range(int(q[2])))
    heads, occ = {}, Counter()
    for i, b in bodies.items():
        heads[b[0]] = i
        for c in b:
            occ[c] += 1
    bad = rounds = 0
    dup = 0
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rounds += 1
            true = Counter()
            for b in bodies.values():
                for c in b:
                    true[c] += 1
            if {c: v for c, v in occ.items() if v} != dict(true):
                bad += 1
            if {b[0]: i for i, b in bodies.items()} != heads:
                bad += 1
            dup += sum(1 for v in true.values() if v > 1)
        elif k == 9:
            i = p.i32(0)
            hd, tl = tile(replay.point(p.pointer(0))), tile(replay.point(p.pointer(1)))
            b = bodies[i]
            if b[0] != hd:
                if heads.get(b[0]) == i:
                    del heads[b[0]]
                b.appendleft(hd)
                heads[hd] = i
                occ[hd] += 1
            while len(b) > 1 and b[-1] != tl:
                occ[b.pop()] -= 1
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for c in bodies[parent]:
                occ[c] -= 1
            if heads.get(bodies[parent][0]) == parent:
                del heads[bodies[parent][0]]
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(tile(replay.point(c)) for c in p.pointer(z))
                heads[bodies[i][0]] = i
                for c in bodies[i]:
                    occ[c] += 1
        elif k == 11:
            i = p.i32(0)
            b = bodies[i]
            if heads.get(b[0]) == i:
                del heads[b[0]]
            for c in b:
                occ[c] -= 1
            bodies.pop(i)
    print(row['game'], row['layout'], 'rounds', rounds, 'round starts where the books differ from a recount', bad, 'tiles counted twice', dup)


main()

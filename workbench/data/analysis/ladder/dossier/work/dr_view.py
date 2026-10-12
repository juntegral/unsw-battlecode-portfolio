# Scratch (diag-drops): prints what happens round by round near one tile of one game.
# For rounds lo..hi: every turn of a dragon whose head starts or ends within <radius> grid tiles of (x, y), with its side
# (0 = the followed team), length, move, pearls eaten, split or death, and the pearls lying within the radius at each
# round start (d = dropped by a death, n = natural).
# Usage: python3 data/analysis/ladder/dossier/work/dr_view.py <O|R> <game> <lo> <hi> <x> <y> [radius]
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import deque
from pathlib import Path


def main():
    who, game, lo, hi, cx, cy = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6])
    rad = int(sys.argv[7]) if len(sys.argv) > 7 else 4
    rows = json.loads(Path('data/analysis/ladder/dossier/work/wk_index.json').read_text())
    row = [r for r in rows if r['who'] == who and r['game'] == game][0]
    root = replay.load(Path(row['replay'])).root()
    text = root.text(0)
    w, h = map(int, text.splitlines()[0].split()[1:3])
    bodies, teams = {}, {}
    for line in text.splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque((int(q[3 + 2 * k]), int(q[4 + 2 * k])) for k in range(int(q[2])))
            teams[i] = 'AB'[int(q[1])]
    focal = row['side']

    def near(p):
        dx, dy = abs(p[0] - cx), abs(p[1] - cy)
        return min(dx, w - dx) + min(dy, h - dy) <= rad

    present = {}
    rnd, actor, log, start, expect = 0, None, [], None, 0

    def flush():
        if actor is not None and lo <= rnd <= hi and log:
            print('  r%d #%d side %d L%d %s: %s' % (rnd, actor, 0 if teams[actor] == focal else 1, start[1], start[0], ' '.join(log)))

    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 3, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            flush()
            rnd, actor, log = p.i32(0), None, []
            if rnd > hi:
                break
            if lo <= rnd:
                print('round', rnd, 'pearls near:', ' '.join('%s(%d,%d)' % (v, c[0], c[1]) for c, v in sorted(present.items()) if near(c)))
        elif k == 1:
            flush()
            actor = p.i32(0)
            b = bodies[actor]
            start = (b[0], len(b))
            log = []
        elif k == 3:
            c = replay.point(p.pointer(0))
            if p.u32(0):
                present[c] = 'd' if expect > 0 else 'n'
                expect = max(0, expect - 1)
            else:
                present.pop(c, None)
                if near(c) or near(start[0]):
                    log.append('eats(%d,%d)' % c)
        elif k == 9:
            i = p.i32(0)
            hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
            b = bodies[i]
            if b[0] != hd:
                b.appendleft(hd)
                if i == actor and (near(hd) or near(start[0])):
                    log.append('to(%d,%d)' % hd)
            while len(b) > 1 and b[-1] != tl:
                b.pop()
        elif k == 10:
            parent, child = p.i32(0), p.i32(4)
            for z, i in enumerate((parent, child)):
                bodies[i] = deque(replay.point(c) for c in p.pointer(z))
                teams[i] = 'AB'[p.u16(8)]
            if near(bodies[parent][0]):
                log.append('splits(#%d L%d, #%d L%d)' % (parent, len(bodies[parent]), child, len(bodies[child])))
        elif k == 11:
            i, reason = p.i32(0), p.u16(4)
            b = bodies.pop(i)
            expect += (len(b) + 1) // 2
            if near(b[0]) and lo <= rnd <= hi:
                why = ('wall', 'own body', 'another body', 'head-on', 'no valid action')[reason]
                if i == actor:
                    log.append('DIES(%s, L%d)' % (why, len(b)))
                else:
                    log.append('kills #%d side %d L%d at (%d,%d)' % (i, 0 if teams[i] == focal else 1, len(b), b[0][0], b[0][1]))
    flush()


main()

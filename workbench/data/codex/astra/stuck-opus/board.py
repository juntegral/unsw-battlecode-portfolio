"""stuck-opus: wide board round a dragon at its turn start. Usage (ROOT): python3 -B data/codex/astra/stuck-opus/board.py <replay> <dragon> <round> [radius=7]
Two chars a cell: content (. free, o pearl, H head, b own body, M/m mate head/body, E/e enemy head/body) then t = dead-end cell
(removed by repeatedly pruning cells with one open side), else a blank. Lists pearls within the box with their age and dead-end depth."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
sys.path.insert(0, 'data/codex/astra/stuck-opus')
from ladder_replay import replay
from collections import deque
from geom import geometry

path, did, rr = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
R = int(sys.argv[4]) if len(sys.argv) > 4 else 7
CX, CY = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (None, None)
root = replay.load(path).root()
G = geometry(root.text(0))
W, H, nb, dead = G['W'], G['H'], G['nb'], G['dead']
bodies, teams = G['bodies'], G['teams']
pearls = {}
rnd = -1
done = False
for ev in root.pointer(3):
    k = ev.u16(0)
    if k not in (0, 1, 3, 9, 10, 11):
        continue
    p = ev.pointer(0)
    if k == 0:
        rnd = p.i32(0)
        if rnd > rr:
            break
    elif k == 1:
        if p.i32(0) == did and rnd == rr:
            b = bodies[did]
            h = b[0]
            hx, hy = h % W, h // W
            if CX is not None:
                hx, hy = CX, CY
            print('r%d dragon %d head (%d,%d) L %d' % (rnd, did, hx, hy, len(b)))
            near = []
            for dy in range(-R, R + 1):
                row = ''
                for dx in range(-R, R + 1):
                    c = ((hy + dy) % H) * W + (hx + dx) % W
                    ch = '.'
                    if c in pearls:
                        ch = 'o'
                        near.append(((hx + dx) % W, (hy + dy) % H, rnd - pearls[c], dead.get(c, 0)))
                    for z, bb in bodies.items():
                        if c in bb:
                            mine = teams[z] == teams[did]
                            ch = ('H' if z == did else 'M' if mine else 'E') if bb[0] == c else ('b' if z == did else 'm' if mine else 'e')
                    if len(sys.argv) > 7:
                        x0, y0 = c % W, c // W
                        ws = ''.join('NESW'[d] for d in range(4) if G['wall'](x0, y0, d))
                        row += '%-6s' % (ch + ('t' if c in dead else '') + ws)
                    else:
                        row += ch + ('t' if c in dead else ' ')
                print('   ' + row)
            print('   pearls (x, y, age, dead-end depth):', near)
            done = True
    elif k == 3:
        pt = replay.point(p.pointer(0))
        c = pt[1] * W + pt[0]
        if p.u32(0):
            pearls[c] = rnd
        else:
            pearls.pop(c, None)
    elif k == 9:
        i = p.i32(0)
        hd, tl = replay.point(p.pointer(0)), replay.point(p.pointer(1))
        hd, tl = hd[1] * W + hd[0], tl[1] * W + tl[0]
        b = bodies[i]
        if b[0] != hd:
            b.appendleft(hd)
        while len(b) > 1 and b[-1] != tl:
            b.pop()
    elif k == 10:
        for z, i in enumerate((p.i32(0), p.i32(4))):
            bodies[i] = deque(pt[1] * W + pt[0] for pt in map(replay.point, p.pointer(z)))
            teams[i] = p.u16(8)
    elif k == 11:
        bodies.pop(p.i32(0))
if not done:
    print('dragon not acting in that round')

"""Game identity by the event stream (rounds, actors, moves, body updates, splits, deaths). Usage (from ROOT): same.py <armA> <armB>"""
import sys, os, glob, hashlib
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
R = os.path.expanduser('~/meow-redteam/solo/runs/')


def sig(path):
    root = replay.load(path).root()
    h = hashlib.sha1()
    n = 0
    first = None
    rnd = -1
    for ev in root.pointer(3):
        k = ev.u16(0)
        if k not in (0, 1, 4, 9, 10, 11):
            continue
        p = ev.pointer(0)
        if k == 0:
            rnd = p.i32(0)
            t = ('r', rnd)
        elif k == 1:
            t = ('a', p.i32(0))
        elif k == 4:
            a = p.pointer(0)
            t = ('m', a.u16(0) if a else -1, tuple(a.pointer(0)) if a and a.u16(0) == 0 and a.pointer(0) is not None else ())
        elif k == 9:
            t = ('b', p.i32(0), replay.point(p.pointer(0)), replay.point(p.pointer(1)))
        elif k == 10:
            t = ('s', p.i32(0), p.i32(4))
        else:
            t = ('d', p.i32(0), p.u16(4))
        h.update(repr(t).encode())
        n += 1
    return h.hexdigest(), n, [root.text(1), root.text(2)]


a, b = sys.argv[1], sys.argv[2]
for d in sorted(glob.glob(R + a + '/*-seed*-side*')):
    e = d.replace('/' + a + '/', '/' + b + '/')
    if not (os.path.exists(d + '/result.txt') and os.path.exists(e + '/result.txt')):
        continue
    x, y = sig(d + '/game.replay'), sig(e + '/game.replay')
    print('%-8s %-8s %-42s %s events %d/%d names %s %s' % (a, b, os.path.basename(d), 'SAME GAME' if x[0] == y[0] else 'different', x[1], y[1], x[2], y[2]))

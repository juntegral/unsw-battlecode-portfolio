#!/usr/bin/env python3
"""trace.py replay [--from R] [--to R] [--every N] : per-round dragon table + deaths/splits."""
import sys, argparse
sys.path.insert(0, 'tools')
from collections import deque
from replay_format import load, point

def run(path, r0, r1, every, quiet=False):
    root = load(path).root()
    dragons = {}
    for line in root.text(0).splitlines():
        f = line.split()
        if f and f[0] == 'DRAGON':
            team, length = int(f[1]), int(f[2]); c = list(map(int, f[3:]))
            dragons[len(dragons)] = {'team': team, 'body': deque(zip(c[::2], c[1::2]))}
    cur = 0
    out = []
    def dump():
        if r0 <= cur <= r1 and (cur % every == 0):
            s = ' | '.join(f"{i}{'AB'[d['team']]}L{len(d['body'])}@{d['body'][0][0]},{d['body'][0][1]}" for i, d in sorted(dragons.items()))
            out.append(f"r{cur}: {s}")
    for ev in root.pointer(3):
        kind, p = ev.u16(0), ev.pointer(0)
        if kind == 0:
            dump(); cur = p.i32(0) + 1
        elif kind == 9:
            d = dragons.get(p.i32(0)); b = d['body']
            b.appendleft(point(p.pointer(0))); tail = point(p.pointer(1))
            while len(b) > 1 and b[-1] != tail: b.pop()
        elif kind == 10:
            par, ch, team = p.i32(0), p.i32(4), p.u16(8)
            dragons[par] = {'team': team, 'body': deque(point(q) for q in p.pointer(0))}
            dragons[ch] = {'team': team, 'body': deque(point(q) for q in p.pointer(1))}
            if r0 <= cur <= r1: out.append(f"  r{cur} SPLIT {par}->{ch} team{'AB'[team]} parentL={len(dragons[par]['body'])} childL={len(dragons[ch]['body'])}")
        elif kind == 11:
            i = p.i32(0); d = dragons.pop(i, None)
            raw = [p.i32(k) for k in (0, 4, 8, 12)]
            out.append(f"  r{cur} DEATH id={i} team={'AB'[d['team']] if d else '?'} len={len(d['body']) if d else '?'} head={d['body'][0] if d else '?'} raw={raw} u16={[p.u16(k) for k in (4,6,8,10)]}")
    dump()
    res = root.pointer(4)
    st = [(res.pointer(s).i32(0), res.pointer(s).i32(4), res.pointer(s).i32(8), res.pointer(s).i32(12)) for s in (0, 1)]
    out.append(f"END rounds={cur} winner={res.u16(6) if res.u16(4)==1 else 'draw'} reason={('elim','limit')[res.u16(2)]} (dragons,longest,total,queen) A={st[0]} B={st[1]}")
    return out

if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('replay'); ap.add_argument('--from', dest='r0', type=int, default=0)
    ap.add_argument('--to', dest='r1', type=int, default=10**9); ap.add_argument('--every', type=int, default=1)
    a = ap.parse_args()
    print('\n'.join(run(a.replay, a.r0, a.r1, a.every)))

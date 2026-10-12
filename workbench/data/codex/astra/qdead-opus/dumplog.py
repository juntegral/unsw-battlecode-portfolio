import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import Counter
root = replay.load(sys.argv[1]).root()
kinds = Counter()
rnd = -1
n = 0
for ev in root.pointer(3):
    k = ev.u16(0)
    kinds[k] += 1
    p = ev.pointer(0)
    if k == 0:
        rnd = p.i32(0)
    if k in (2, 5, 6, 7, 8):
        for z in range(3):
            try:
                t = p.text(z)
            except Exception:
                t = ''
            if t and ('QDK' in t or 'QHOLD' in t or n < 3):
                n += 1
                print(rnd, k, z, repr(t[:200]))
print(kinds)

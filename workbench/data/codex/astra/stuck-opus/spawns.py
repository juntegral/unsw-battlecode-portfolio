"""stuck-opus: pearl births and removals per 100 rounds in one replay. Usage (ROOT): python3 -B data/codex/astra/stuck-opus/spawns.py <replay>"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import Counter
root = replay.load(sys.argv[1]).root()
rnd = -1
born, gone = Counter(), Counter()
for ev in root.pointer(3):
    k = ev.u16(0)
    p = ev.pointer(0)
    if k == 0:
        rnd = p.i32(0)
    elif k == 3:
        (born if p.u32(0) else gone)[max(rnd, 0) // 100] += 1
print('rounds', rnd, 'pearl births per 100 rounds', dict(sorted(born.items())), 'removals', dict(sorted(gone.items())))

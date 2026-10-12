# Scratch (diag-spawn): look at the header and the event kinds of one replay.
# Usage: python3 data/analysis/ladder/dossier/work/sp_peek.py <replay path> [events to print]
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import Counter

path = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 60
root = replay.load(path).root()
text = root.text(0)
lines = text.splitlines()
print(len(lines), 'header lines')
kinds = Counter(l.split()[0] for l in lines if l.split())
print(kinds)
for l in lines[:6]:
    print(l[:200])
for k in kinds:
    ex = [l for l in lines if l.startswith(k)][:3]
    print(k, ex)
print('format', root.u32(0), 'botA', root.text(1), 'botB', root.text(2))
ec = Counter()
shown = 0
rnd = 0
for ev in root.pointer(3):
    k = ev.u16(0)
    ec[replay.EVENT_NAMES[k] if k < len(replay.EVENT_NAMES) else k] += 1
    p = ev.pointer(0)
    if k == 0:
        rnd = p.i32(0)
    if k == 2 and shown < n:
        shown += 1
        print('pearlCountdown r', rnd, 'dwords', p.dwords, 'pwords', p.pwords,
              [p.i32(o) for o in range(0, 8 * p.dwords, 4)],
              [replay.point(p.pointer(z)) if p.pointer(z) is not None and hasattr(p.pointer(z), 'i32') else None for z in range(p.pwords)])
print(ec)

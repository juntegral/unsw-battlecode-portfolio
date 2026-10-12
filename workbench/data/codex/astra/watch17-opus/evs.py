"""watch17-opus: event kinds in a replay and any text near a round. Usage (from ROOT): python3 -B .../evs.py <replay> <round>"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import Counter
root = replay.load(sys.argv[1]).root()
N = replay.EVENT_NAMES
print(N)
c = Counter()
rnd = -1
want = int(sys.argv[2])
for ev in root.pointer(3):
    k = N[ev.u16(0)]
    c[k] += 1
    p = ev.pointer(0)
    if k == 'roundStart':
        rnd = p.i32(0)
    elif rnd == want and k not in ('dragonUpdate', 'turnStart', 'dragonAction', 'tileChange', 'dragonSplit', 'dragonDeath'):
        try:
            print(rnd, k, [p.text(i) for i in range(2)])
        except Exception as ex:
            print(rnd, k, 'unreadable', repr(ex)[:80])
print(c)

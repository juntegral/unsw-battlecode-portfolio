# Scratch (diag-hungry): prints the map header of one local replay and the event kinds seen.
# Usage: python3 data/analysis/ladder/dossier/work/hg_peek.py <run dir name under solo/runs/m3b7>
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'tools')
from ladder_replay import replay
from collections import Counter
from pathlib import Path

RUNS = '~/meow-redteam/solo/runs/m3b7/'


def main():
    root = replay.load(Path(RUNS + sys.argv[1] + '/game.replay')).root()
    text = root.text(0)
    lines = text.splitlines()
    kinds = Counter(l.split()[0] for l in lines if l.split())
    print(lines[:6])
    print(kinds)
    for want in ('TILE', 'EDGE', 'DRAGON', 'PORTAL'):
        print(want, [l for l in lines if l.startswith(want)][:4])
    ev = Counter()
    first = {}
    for n, e in enumerate(root.pointer(3)):
        k = e.u16(0)
        ev[k] += 1
        first.setdefault(k, n)
    print(sorted(ev.items()), first)
    print('names', list(enumerate(replay.EVENT_NAMES)))
    print('bots', root.text(1), '|', root.text(2))


main()

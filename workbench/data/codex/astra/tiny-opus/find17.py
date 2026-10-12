"""Existing local games of the live bot (mD17 binary) against m3base on the eight check maps."""
import json, sys
from pathlib import Path
RUNS = Path.home() / 'meow-redteam/solo/runs'
MAPS = ('ladder_tower_defense_1', 'ladder_stripes_1', 'ladder_default_1', 'ladder_devil_1', 'ladder_maze_1', 'ladder_weakhold_1', 'gx_open_24x12_910901', 'gx_rooms_24x12_911001')
for m in MAPS:
    for f in sorted(RUNS.glob('*/%s-seed*-side*/result.json' % m)):
        try: j = json.loads(f.read_text())
        except Exception: continue
        a, b = j['botA'].split('/')[-2], j['botB'].split('/')[-2]
        if {a, b} == {'mD17', 'm3base'} or (len(sys.argv) > 1 and (sys.argv[1] in a or sys.argv[1] in b)):
            print(f.parent.parent.name, f.parent.name, a, 'v', b, j['line'][:70])

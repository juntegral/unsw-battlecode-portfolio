"""wastel.py <arm> ...: waste.py's event count on local runs, whole game, our side and the other side. Run from ROOT."""
import sys, re
sys.dont_write_bytecode = True
sys.argv, args = sys.argv[:1], sys.argv[1:]
sys.path.insert(0, 'data/codex/astra/trauma-opus')
from pathlib import Path
import importlib.util
spec = importlib.util.spec_from_file_location('w', 'data/codex/astra/trauma-opus/waste.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)
RUNS = Path.home() / 'meow-redteam/solo/runs'
for arm in args:
    for folder in sorted((RUNS / arm).glob('*-seed*-side[01]')):
        if not (folder / 'result.txt').exists():
            continue
        k = int(folder.name[-1])
        out, last = w.count(folder / 'game.replay', k)
        print('%-14s %-40s us %2d (r<=100 %d)  other %2d' % (arm, folder.name, len(out[0]), sum(1 for r in out[0] if r <= 100), len(out[1])))

import sys,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('prior_analysis','data/codex/astra/sweep/0410/loss1/analyze.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
a.OUT=Path(__file__).resolve().parent
a.GAMES=[(1488845,1488846),(1488845,1488847)]
for bid,gid in a.GAMES:a.run(bid,gid)

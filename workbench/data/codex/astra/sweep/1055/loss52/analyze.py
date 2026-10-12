import sys, importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('prior_scan','data/codex/astra/sweep/0630/loss1/analyze.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.OUT=Path(__file__).resolve().parent
m.SRC=Path('data/online/smoke/one14-c1-old')
if __name__=='__main__':
    for gid in (1517694,1517697,1517698):m.scan(gid)

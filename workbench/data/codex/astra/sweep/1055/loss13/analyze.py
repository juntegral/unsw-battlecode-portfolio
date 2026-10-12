import sys, importlib.util, inspect
from pathlib import Path
sys.dont_write_bytecode=True
p=Path('data/codex/astra/sweep/0410/loss1/analyze.py')
s=importlib.util.spec_from_file_location('existing_loss_reader',p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.OUT=Path(__file__).resolve().parent
source=inspect.getsource(m.run).replace("p=Path(f'data/online/live-one1/b{bid}/M{gid}.replay')", "p=Path(f'data/online/smoke/one12-k1-old/M{gid}.replay')")
source=source.replace("lr.scan(p,meta,'ranked',set())", "lr.scan(p,meta,'one12-k1-old',set())")
exec(compile(source,str(p),'exec'),m.__dict__)
for gid in (1504489,1504492,1504493):m.run(None,gid)

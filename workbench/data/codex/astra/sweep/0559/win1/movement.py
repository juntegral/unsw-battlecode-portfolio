import sys
sys.dont_write_bytecode=True
import importlib.util,json
from pathlib import Path
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('move_audit','data/codex/astra/audit-move/audit.py')
audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
rows=[]
for gid in (1494956,1494960,1494963,1494966,1494967):
    path=(Path('data/online/smoke/one8-p1-old')/f'M{gid}.replay').resolve()
    meta=json.loads(path.with_name(f'game-{gid}.json').read_text())
    root=audit.replay.load(path).root()
    row=audit.census(path,meta,root)
    rows.append(row)
    print(gid,json.dumps(row['counts']),flush=True)
(OUT/'movement.json').write_text(json.dumps(rows,ensure_ascii=False)+'\n')

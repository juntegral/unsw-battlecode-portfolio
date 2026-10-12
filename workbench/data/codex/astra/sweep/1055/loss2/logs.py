import sys,json
sys.dont_write_bytecode=True
sys.path.insert(0,'data/analysis/ladder/dossier/local')
from replay_format import load
from pathlib import Path
O=Path('data/codex/astra/sweep/1055/loss2')
for gid in [1501666,1501667,1501668]:
 root=load(f'data/online/smoke/one12-c1-old/M{gid}.replay').root();r=-1;logs=[]
 for e in root.pointer(3):
  k=e.u16(0)
  if k==0:r=e.pointer(0).i32(0)
  if k==6:
   p=e.pointer(0);logs.append([r,p.i32(0),p.text(0)])
 (O/f'{gid}-logs.json').write_text(json.dumps(logs));print(gid,len(logs),logs[:5],flush=True)

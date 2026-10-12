import sys,json,importlib.util
from pathlib import Path
from collections import Counter
sys.dont_write_bytecode=True
spec=importlib.util.spec_from_file_location('codec',Path('../battlecode/work/card_42_check.py'));codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
sys.path.insert(0,'data/analysis/ladder/dossier/local')
from scoreboard import load_replay
out={}
for gid,death in [(1488842,115),(1488844,34)]:
 root=load_replay(Path(f'data/online/live-one1/b1488840/M{gid}.replay')).root();w,h=map(int,root.text(0).splitlines()[0].split()[1:]);key=codec.make_key(w,h,2);streams={};opened={};counts=Counter();r=-1;team={};examples=[]
 for l in root.text(0).splitlines():
  q=l.split()
  if q and q[0]=='DRAGON':team[len(team)]=int(q[1])
 for ev in root.pointer(3):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:r=p.i32(0)
  elif k==10:team[p.i32(4)]=p.u16(8)
  elif k==12 and r>=death and team[p.i32(0)]==0:
   wire=p.u64(16)
   if wire not in opened:opened[wire]=codec.unseal(key,wire,streams)
   plain=opened[wire]
   if plain is None:counts['unreadable']+=1;continue
   kind=codec.parse(plain)[0]
   if kind not in ('leader','queen'):continue
   state=(plain>>(26 if kind=='leader' else 24))&3
   counts[f'{kind}_state{state}']+=1
   if state&1:examples.append([r,p.i32(0),kind,state])
 out[gid]=dict(counts=counts,death_claim_examples=examples[:10]);print(gid,out[gid])
Path(__file__).with_name('signals.json').write_text(json.dumps(out,indent=2))

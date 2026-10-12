import sys
sys.dont_write_bytecode=True
from analyze import OUT,read,point
from pathlib import Path
import json
cases=[(1471457,5,14,[17],[2478]),(1471458,33,41,[22,35],[2070]),(1471460,59,64,[13,16],[35]),
       (1471456,68,70,[2,18],[261]),(1471458,93,94,[42],[2085,2114]),
       (1471462,7,15,[23],[3342,3596,3597]),(1471465,48,56,[5],[672,615,676]),(1471459,7,15,[1],[233,140])]
lines=[]
for gid,lo,hi,ids,cells in cases:
 g=json.loads((OUT/f'g{gid}.json').read_text());r=read(Path('data/online/smoke')/(g['label']+'-old')/f'M{gid}.replay');w=g['w']
 lines.append(f"\nGAME {gid} {g['label']} {g['map']} r{lo}..{hi} ids={ids} cells={[(c%w,c//w) for c in cells]}")
 rnd=-1;actor=None
 for ev in r.pointer(3):
  k=ev.u16(0)
  if k not in (0,1,3,9,10,11):continue
  p=ev.pointer(0)
  if k==0:rnd=p.i32(0);actor=None
  elif k==1:actor=p.i32(0)
  if not lo<=rnd<=hi:continue
  if k==3:
   xy=point(p.pointer(0));c=xy[1]*w+xy[0]
   if c in cells:lines.append(f"r{rnd} {'BIRTH' if p.u32(0) else 'EAT'} {xy} actor={actor}")
  elif k==9 and p.i32(0) in ids:lines.append(f'r{rnd} MOVE id={p.i32(0)} head={point(p.pointer(0))} tail={point(p.pointer(1))}')
  elif k==10 and p.i32(0) in ids:lines.append(f'r{rnd} SPLIT parent={p.i32(0)} child={p.i32(4)}')
  elif k==11 and p.i32(0) in ids:lines.append(f'r{rnd} DEATH id={p.i32(0)} reason={p.u16(4)}')
(OUT/'moments.txt').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))

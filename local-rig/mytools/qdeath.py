import sys
sys.path.insert(0,'tools'); sys.path.insert(0,'mytools')
from replay_format import load, point
import trace
path=sys.argv[1]; q=int(sys.argv[2]); R=int(sys.argv[3])
root=load(path).root(); cur=0; last=None; lines=[]
for ev in root.pointer(3):
    k,p=ev.u16(0),ev.pointer(0)
    if k==0: cur=p.i32(0)+1
    if cur in (R-1,R):
        if k==1: last=p.i32(0)
        if k==9: lines.append((cur,'UPD',p.i32(0),point(p.pointer(0))))
        if k==10: lines.append((cur,'SPLIT',p.i32(0),p.i32(4)))
        if k==11: lines.append((cur,'DEATH',p.i32(0),last))
# find killer: the dragon whose turn it was when queen died
killer=None
for l in lines:
    if l[1]=='DEATH' and l[2]==q: killer=l[3]
print('queen',q,'died r',R,'during turn of dragon',killer)
for l in lines:
    if l[2] in (q,killer) or (l[1]=='SPLIT' and l[3]==killer): print('  ',l)
out=trace.run(path,R-2,R-1,1)
import re
for o in out:
    if o.startswith('r'):
        for part in o.split(' | '):
            m=re.search(r'(\d+)([AB])L(\d+)@(\d+),(\d+)',part)
            if m and int(m.group(1)) in (q,killer): print('  state',o.split(':')[0],part.strip()[-20:])

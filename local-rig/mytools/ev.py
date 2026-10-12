import sys
sys.path.insert(0,'tools')
from replay_format import load, point
root = load(sys.argv[1]).root(); r0=int(sys.argv[2]); r1=int(sys.argv[3]); cur=0
from collections import Counter
c=Counter()
for ev in root.pointer(3):
    k,p=ev.u16(0),ev.pointer(0); c[k]+=1
    if k==0: cur=p.i32(0)+1
    if r0<=cur<=r1:
        if k==9: print(cur,'UPD id',p.i32(0),'head',point(p.pointer(0)),'tail',point(p.pointer(1)),'face',p.u16(4), 'u16s',[p.u16(i) for i in (4,6,8,10,12,14)])
        elif k==11: print(cur,'DEATH',[p.i32(i) for i in (0,4,8,12)])
        elif k==10: print(cur,'SPLIT',p.i32(0),p.i32(4))
        elif k==3: print(cur,'TILE',point(p.pointer(0)),p.bit(0))
        elif k==2: pass
        elif k==0: print('--- round',cur)
        else:
            print(cur,'KIND',k,[p.i32(i) for i in (0,4,8,12)] if p is not None else None)
print(c)

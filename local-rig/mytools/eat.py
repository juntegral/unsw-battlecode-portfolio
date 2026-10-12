import sys
sys.path.insert(0,'tools')
from replay_format import load, point
for path in sys.argv[2:]:
    root = load(path).root(); every=int(sys.argv[1])
    team={}; n=0
    for line in root.text(0).splitlines():
        f=line.split()
        if f and f[0]=='DRAGON': team[n]=int(f[1]); n+=1
    eat=[0,0]; cur=0; last=None; split=[0,0]; dead=[0,0]; rows=[]
    for ev in root.pointer(3):
        k,p=ev.u16(0),ev.pointer(0)
        if k==0:
            cur=p.i32(0)+1
            if cur%every==0: rows.append((cur,tuple(eat),tuple(split),tuple(dead)))
        elif k==1: last=p.i32(0)
        elif k==3 and not p.bit(0) and last is not None: eat[team[last]]+=1
        elif k==10: team[p.i32(4)]=p.u16(8); split[p.u16(8)]+=1
        elif k==11: dead[team[p.i32(0)]]+=1
    print(path)
    for r in rows: print('  r%d eaten A=%d B=%d | splits A=%d B=%d | deaths A=%d B=%d'%(r[0],r[1][0],r[1][1],r[2][0],r[2][1],r[3][0],r[3][1]))

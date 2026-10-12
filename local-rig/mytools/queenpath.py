import sys, re
sys.path.insert(0,'mytools'); sys.path.insert(0,'tools')
import trace
path=sys.argv[1]; q=sys.argv[2]
out=trace.run(path,0,10**9,1)
pos=[]; 
for o in out:
    if o.startswith('r'):
        m=re.search(r'(?:^|\| |: )'+q+r'[AB]L(\d+)@(\d+),(\d+)',o)
        r=int(o.split(':')[0][1:])
        if m: pos.append((r,int(m.group(1)),(int(m.group(2)),int(m.group(3)))))
# first round from which positions repeat with period 4
start=None
for i in range(len(pos)-8):
    if all(pos[j][2]==pos[j+4][2] for j in range(i,min(i+8,len(pos)-4))) and pos[i][1]>=22:
        start=pos[i][0]; break
print(path,'queen',q,'first L>=22 at r',next((r for r,L,_ in pos if L>=22),None),'| cycle of 4 stops from r',start,'| last seen r',pos[-1][0],'L',pos[-1][1])
if start is not None:
    i=[k for k,(r,_,_) in enumerate(pos) if r==start][0]
    print('   stops:',[p[2] for p in pos[i:i+4]])

import sys
f=sys.argv[1]
lines=open(f).read().split('\n')
W=H=0;kind={};pid={};gap={};occ={}
for l in lines:
    p=l.split()
    if not p: continue
    if p[0]=='MAP': W,H=int(p[1]),int(p[2])
    if p[0]=='EDGE': kind[int(p[1])]=int(p[2]); pid[int(p[1])]=int(p[3])
    if p[0]=='TILE': gap[(int(p[1]),int(p[2]))]=(int(p[3]),int(p[4]))
    if p[0]=='DRAGON':
        t=p[1]; n=int(p[2]); pts=list(map(int,p[3:]))
        for j in range(n): occ[(pts[2*j],pts[2*j+1])]=('A' if t=='0' else 'B') if j==0 else ('a' if t=='0' else 'b')
rl=W+1
def Hk(x,y): return kind.get((2*y)*rl+x,0)
def Vk(x,y): return kind.get((2*y+1)*rl+x,0)
def tch(x,y):
    if (x,y) in occ: return occ[(x,y)]
    mn,mx=gap.get((x,y),(0,0))
    if mx==0: return ' '
    if mx==1: return '@'
    if mx<=10: return 'o'
    if mx<=50: return ':'
    return '.'
for y in range(H+1):
    print(''.join('+'+('-' if Hk(x,y)==1 else ('~' if Hk(x,y)==2 else ' ')) for x in range(W))+'+')
    if y==H: break
    print(''.join(('|' if Vk(x,y)==1 else ('~' if Vk(x,y)==2 else ' '))+tch(x,y) for x in range(W))+('|' if Vk(W,y)==1 else ('~' if Vk(W,y)==2 else ' ')))

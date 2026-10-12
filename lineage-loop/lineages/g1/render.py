import sys
L=open(sys.argv[1]).read().split('\n')
W=H=0;E={};T={};D=[]
for l in L:
  p=l.split()
  if not p: continue
  if p[0]=='MAP': W,H=int(p[1]),int(p[2])
  if p[0]=='EDGE': E[int(p[1])]=(int(p[2]),int(p[3]))
  if p[0]=='TILE': T[(int(p[1]),int(p[2]))]=int(p[4])
  if p[0]=='DRAGON':
    n=int(p[2]);D+=[(int(p[3+2*i]),int(p[4+2*i]),p[1]) for i in range(n)]
def e(i):
  k=E.get(i,(0,-1))
  return k[0]
out=[]
for y in range(H+1):
  row=''
  for x in range(W+1):
    hk=e((2*y)*(W+1)+x)
    row+='+'+('--' if hk==1 else ('pp' if hk==2 else '  '))
  out.append(row)
  if y==H: break
  row=''
  for x in range(W+1):
    vk=e((2*y+1)*(W+1)+x)
    c='|' if vk==1 else ('P' if vk==2 else ' ')
    t='  '
    if x<W:
      t=' .' if T.get((x,y),0)>0 else '  '
      for dx,dy,tm in D:
        if (dx,dy)==(x,y): t=' '+('a' if tm=='0' else 'b')
    row+=c+t
  out.append(row)
print('\n'.join(out))

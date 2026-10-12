exec(open('data/codex/astra/sweep/1055/loss17/details.py').read().split('for gid,bid')[0])
from collections import deque
for gid,bid in [(1502778,1502774),(1507592,1507592)]:
 g=json.loads((D/f'{gid}.json').read_text());w=g['width'];h=g['height'];root=scoreboard.load_replay(Path(f'data/online/live-one1/b{bid}/M{gid}.replay')).root();raw=[tuple(map(int,l.split()[1:4])) for l in root.text(0).splitlines() if l.startswith('EDGE ')];geo=Geo(w,h,raw)
 xy=lambda c:(c%w,c//w)
 for t in g['queen_turns'][-3:]:
  q=t['id']; hd=t['body'][0];occ={c:int(i) for i,b in t['scene'].items() for c in b};targets=[n for k,n in geo.moves[hd] if k!=1 and n not in occ]; print(gid,t['round'],'targets',list(map(xy,targets)))
  for i,b in t['scene'].items():
   if g['teams'][i]==g['ours'] or not geo.visible(hd,b[0]):continue
   seen=sum(geo.visible(hd,c) for c in b);print('enemy',i,'L',len(b),'seen',seen,'at',xy(b[0]))
   queue=deque([(b[0],[b[0]])]);visited={b[0]}
   while queue:
    c,path=queue.popleft()
    if len(path)>7:continue
    if c in targets: print(' reaches',xy(c),'dist',len(path)-1,'path',list(map(xy,path)))
    for n in geo.adj[c]:
     if n in visited or (n in occ and n!=hd):continue
     visited.add(n);queue.append((n,path+[n]))
  cx,cy=xy(hd);lines=[]
  for y in range(cy-3,cy+4):
   upper='';row=''
   for x in range(cx-3,cx+4):
    c=(y%h)*w+x%w;i=occ.get(c);k=t['scene'][str(i)].index(c) if i is not None else -1
    att=581 if gid==1502778 else 87
    ch=('*' if c in t['pearls'] else '.') if i is None else ('Q' if k==0 else 'q') if i==q else ('X' if k==0 else 'x') if i==att else ('A' if k==0 else 'a') if g['teams'][str(i)]==g['ours'] else ('E' if k==0 else 'e')
    upper+='+'+('-' if geo.moves[c][0][0]==1 else 'O' if geo.moves[c][0][0]==2 else ' ')
    row+=('|' if geo.moves[c][3][0]==1 else 'O' if geo.moves[c][3][0]==2 else ' ')+ch
   lines.extend([upper+'+',row+('|' if geo.moves[c][1][0]==1 else 'O' if geo.moves[c][1][0]==2 else ' ')])
  lines.append(''.join('+'+('-' if geo.moves[((cy+3)%h)*w+(x%w)][2][0]==1 else 'O' if geo.moves[((cy+3)%h)*w+x%w][2][0]==2 else ' ') for x in range(cx-3,cx+4))+'+')
  (D/f'grid-{gid}-{t["round"]}.txt').write_text('\n'.join(lines))

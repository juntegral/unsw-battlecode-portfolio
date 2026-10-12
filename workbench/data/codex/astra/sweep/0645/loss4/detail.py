exec(open('data/codex/astra/sweep/0645/loss4/analyze.py').read().split('for gid in (')[0])
for gid in (1498748,1498751):
 d=json.loads((OUT/f'{gid}.json').read_text()); w,h=d['w'],d['h']; q=d['queens'][0]; att=95 if gid==1498748 else 912
 root=load_replay(ROOT/f'data/online/smoke/one11-p1-old/M{gid}.replay').root();raw=[tuple(map(int,l.split()[1:4])) for l in root.text(0).splitlines() if l.startswith('EDGE ')];g=Geo(w,h,raw)
 print('\n',gid)
 for t in d['queen_last3']:
  bodies={int(i):b for i,b in t['bodies'].items()};hd=bodies[q][0]; x,y=hd%w,hd//w; occ={c:i for i,b in bodies.items() for c in b}; heads={b[0]:i for i,b in bodies.items()}; ps=set(t['pearls'])
  print('r',t['r'],'head',x,y,'action',t['action'])
  for dy in range(-3,4):
   cells=[((y+dy)%h)*w+(x+dx)%w for dx in range(-3,4)]
   print('+'+'+'.join('---' if g.moves[c][0][0]==1 else '   ' for c in cells)+'+')
   s=''
   for c in cells:
    i=occ.get(c);ch='Q' if i==q and c==hd else 'q' if i==q else 'X' if i==att and c==bodies[att][0] else 'x' if i==att else ('A' if c in heads else 'a') if i is not None and d['teams'][str(i)]==0 else ('E' if c in heads else 'e') if i is not None else '*' if c in ps else '.'
    s+=('|' if g.moves[c][3][0]==1 else ' ')+f' {ch} '
   print(s+('|' if g.moves[cells[-1]][1][0]==1 else ' '))
  print('+'+'+'.join('---' if g.moves[c][2][0]==1 else '   ' for c in cells)+'+')
  for dr,(k,z) in zip('NESW',g.moves[hd]):print(dr,'wall' if k==1 else 'portal' if k==2 else '',(z%w,z//w),'occupant',occ.get(z),'len',len(bodies.get(occ.get(z),[])))
  print('nearheads',[(i,(b[0]%w,b[0]//w),len(b)) for i,b in bodies.items() if b[0] in g.window(hd)])

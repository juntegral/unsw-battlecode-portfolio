exec(open('data/codex/astra/sweep/0559/loss2/detail.py').read().split('for gid in (')[0])
outs=[]
for gid in (1494957,1494958,1494959):
 d=json.loads((OUT/f'{gid}-detail.json').read_text());base=json.loads((OUT/f'{gid}-base.json').read_text());w,h=d['w'],d['h'];q=base['queens']['us'];atk=next(z['actor'] for z in base['deaths'] if z['id']==q)
 raw=[tuple(map(int,x.split()[1:4])) for x in base['text'].splitlines() if x.startswith('EDGE ')];g=cr.Geometry(w,h,raw)
 outs.append(f'게임 {gid}, Q={q}, X={atk}; 각 판면은 여왕 차례 시작, 북쪽 위. Q/q=여왕 머리/몸, X/x=공격자, A/a=다른 아군, B/b=다른 적, *=진주, .=빈칸, ─│=켈프, P=포털. 좌표는 0부터. [M]')
 grids=[]
 for t in d['queen']:
  hd=t['start'][0];cx,cy=hd%w,hd//w;occ={c:(int(i),k) for i,bb in t['bodies'].items() for k,c in enumerate(bb)}
  lines=[]
  for dy in range(-3,4):
   top='';row=''
   for dx in range(-3,4):
    x,y=(cx+dx)%w,(cy+dy)%h;c=y*w+x;kn=g.moves[c][0][0];kw=g.moves[c][3][0]
    top+='+'+('─' if kn==1 else 'P' if kn==2 else ' ')
    sym='*' if c in t['pearls'] else '.'
    if c in occ:
     i,k=occ[c];sym=('Q' if i==q else 'X' if i==atk else 'A' if d['teams'][str(i)]==0 else 'B');sym=sym.lower() if k else sym
    row+=('│' if kw==1 else 'P' if kw==2 else ' ')+sym
   lines+=[top+'+',row+('│' if g.moves[c][1][0]==1 else 'P' if g.moves[c][1][0]==2 else ' ')]
  bot=''
  for dx in range(-3,4):
   c=((cy+3)%h)*w+(cx+dx)%w;ks=g.moves[c][2][0];bot+='+'+('─' if ks==1 else 'P' if ks==2 else ' ')
  lines.append(bot+'+')
  grids.append([f"r{t['round']} Q({cx},{cy}) L{len(t['start'])}"]+lines)
  print(gid,t['round'],'Q',cx,cy,'near bodies',[(i,len(bb),(bb[0]%w,bb[0]//w)) for i,bb in t['bodies'].items() if g.visible(hd,bb[0])])
  print('adj',[(k,kind,(dest%w,dest//w),occ.get(dest),dest in t['pearls']) for k,(kind,dest) in enumerate(g.moves[hd])])
 outs.append('```text\n'+'\n'.join('    '.join(z.ljust(24) for z in rows) for rows in zip(*grids))+'\n```')
(OUT/'boards.md').write_text('\n\n'.join(outs)+'\n')

import sys,json,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('cr','data/analysis/ladder/losses/counts/count_replays.py');cr=importlib.util.module_from_spec(spec);spec.loader.exec_module(cr)
boards=[]
for gid in (1497389,1497390,1496711):
 b=json.loads((OUT/f'{gid}-base.json').read_text());d=json.loads((OUT/f'{gid}-detail.json').read_text());w,h=d['w'],d['h'];qid=b['queens']['us'];qd=next(x for x in b['deaths'] if x['id']==qid);atk=qd['actor'] if qd['actor']!=qid else qd['hit'];geo=cr.Geometry(w,h,[tuple(map(int,x.split()[1:4])) for x in b['text'].splitlines() if x.startswith('EDGE ')])
 print('\nGAME',gid,w,h,'qdeath',qd,'theirQdeath',[x for x in b['deaths'] if x['id']==b['queens']['them']]);print('final bodies',d['final']);print('Q positions',sorted(set(d['enemy_positions'].values())))
 print('snaps',[(r,b['snapshots'].get(str(r))) for r in (0,1,10,25,49,50,100,130,132,200,250,269,300,350,400,425,450,475,499)])
 print('ourlongdeaths',[x for x in b['deaths'] if x['side']=='us' and x['length']>=10])
 for t in d['attacker']:
  if t['id'] in (atk,qid) or any(z[0]==atk or z[1]==atk for z in t['splits']):print('focus', {k:v for k,v in t.items() if k not in ('bodies','pearls')})
 grids=[]
 for t in d['queen']:
  hd=t['start'][0];cx,cy=hd%w,hd//w;occ={c:(int(i),k) for i,bb in t['bodies'].items() for k,c in enumerate(bb)};lines=[]
  for dy in range(-3,4):
   top='';row=''
   for dx in range(-3,4):
    x,y=(cx+dx)%w,(cy+dy)%h;c=y*w+x;kn=geo.moves[c][0][0];kw=geo.moves[c][3][0];top+='+'+('─' if kn==1 else 'P' if kn==2 else ' ');sym='*' if c in t['pearls'] else '.'
    if c in occ:
     i,k=occ[c];sym='Q' if i==qid else 'X' if i==atk else 'A' if d['teams'][str(i)]==d['own'] else 'B';sym=sym.lower() if k else sym
    row+=('│' if kw==1 else 'P' if kw==2 else ' ')+sym
   lines.extend([top+'+',row+('│' if geo.moves[c][1][0]==1 else 'P' if geo.moves[c][1][0]==2 else ' ')])
  bot=''
  for dx in range(-3,4):
   c=((cy+3)%h)*w+(cx+dx)%w;ks=geo.moves[c][2][0];bot+='+'+('─' if ks==1 else 'P' if ks==2 else ' ')
  lines.append(bot+'+');grids.append([f"r{t['round']} Q({cx},{cy}) L{len(t['start'])}"]+lines)
  print('ADJ',t['round'],[(k,kind,(n%w,n//w),occ.get(n)) for k,(kind,n) in enumerate(geo.moves[hd])])
 boards.append(f'[M] {gid}, 여왕 #{qid}; X={atk if atk is not None else "없음"}.\n\n```text\n'+'\n'.join('    '.join(z.ljust(24) for z in rows) for rows in zip(*grids))+'\n```')
(OUT/'boards.md').write_text('\n\n'.join(boards)+'\n')

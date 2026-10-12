import sys,json,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter,deque
ROOT=Path.cwd();P=ROOT/'data/codex/astra/sweep/1055/loss23';sys.path.insert(0,str(ROOT/'tools'));import ladder_replay as lr
spec=importlib.util.spec_from_file_location('counts',ROOT/'data/analysis/ladder/losses/counts/count_replays.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
boards=[]
for gid in (1510790,1510791,1510793):
 d=json.loads((P/f'{gid}.json').read_text());ts=json.loads((P/f'{gid}-turns.json').read_text());q=d['queens']['us'];a=d['qdeath']['actor'];w=d['w'];h=d['h'];teams=d['teams'];rnd=d['qdeath']['round']
 root=lr.replay.load(ROOT/f'data/online/smoke/one13-c2-old/M{gid}.replay').root();raw=[tuple(map(int,l.split()[1:4])) for l in root.text(0).splitlines() if l.startswith('EDGE ')];g=m.Geometry(w,h,raw)
 print('\nGAME',gid)
 for t in d['last_qturns']:
  st=t['state']; head=t['body'][0];cx=head%w;cy=head//w;cells={c:('Q' if int(i)==q else 'X' if int(i)==a else 'A' if teams[i]==0 else 'B') if n==0 else ('q' if int(i)==q else 'x' if int(i)==a else 'a' if teams[i]==0 else 'b') for i,b in st.items() for n,c in enumerate(b)}
  grid=[]
  for dy in range(-3,4):
   top='';row=''
   for dx in range(-3,4):
    c=((cy+dy)%h)*w+(cx+dx)%w; kn=g.moves[c][0][0];kw=g.moves[c][3][0]
    top+='+'+('-' if kn==1 else 'P' if kn==2 else ' ')
    row+=('|' if kw==1 else 'P' if kw==2 else ' ')+cells.get(c,'*' if c in t['pearls'] else '.')
   grid.extend([top+'+',row+('|' if g.moves[c][1][0]==1 else 'P' if g.moves[c][1][0]==2 else ' ')])
  bot=''
  for dx in range(-3,4):
   c=((cy+3)%h)*w+(cx+dx)%w;kind=g.moves[c][2][0];bot+='+'+('-' if kind==1 else 'P' if kind==2 else ' ')
  grid.append(bot+'+')
  board='\n'.join(grid);print('r',t['round'],'head',(cx,cy),'move',t['dirs']);print(board)
  boards.append(dict(gid=gid,round=t['round'],head=[cx,cy],board=board,dirs=t['dirs']))
  print('visible',[(i,len(b),[b[0]%w,b[0]//w]) for i,b in st.items() if g.visible(head,b[0])]);print('neighbors',[(z,kind,[dest%w,dest//w],[(i,b.index(dest)) for i,b in st.items() if dest in b]) for z,(kind,dest) in enumerate(g.moves[head])])
 snaps=d['snapshots'];after=[int(r) for r,s in snaps.items() if s['us']['total']>=s['them']['total']];qlost=rnd
 def score(s,side):
  z=s[side];return (int(z['alive']>0),z['queen_length'],z['longest'],z['total'])
 nonloss=[int(r) for r,s in snaps.items() if score(s,'us')>=score(s,'them')]
 print('total deficit permanent',max(after)+1 if after else 0,'score deficit permanent',max(nonloss)+1 if nonloss else 0)
 if gid==1510790:
  for i in sorted({t['id'] for t in ts if t['side']==0 and len(t['body'])>=8}):
   own=[t for t in ts if t['id']==i]; print('long',i,'max',max(len(t['body']) for t in own),'r400+',dict(Counter('eat' if t['eaten'] else 'split' if t['split'] else 'noeat' for t in own if t['round']>=400)), 'end',[(c%w,c//w) for c in own[-1]['end']])
 for lo,hi in [(0,100),(101,rnd),(rnd+1,d['last_round'])]:
  print('band',lo,hi, {s:dict(turns=sum(t['side']==s and lo<=t['round']<=hi for t in ts),eat=sum(t['eaten'] for t in ts if t['side']==s and lo<=t['round']<=hi),split=sum(bool(t['split']) for t in ts if t['side']==s and lo<=t['round']<=hi),nomeal_move=sum(bool(t['steps']) and not t['eaten'] for t in ts if t['side']==s and lo<=t['round']<=hi)) for s in (0,1)})
(P/'boards.json').write_text(json.dumps(boards,ensure_ascii=False,indent=2))

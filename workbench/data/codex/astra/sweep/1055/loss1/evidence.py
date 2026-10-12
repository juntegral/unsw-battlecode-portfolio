import sys,json
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
from ladder_replay import edge_id,canonical_edges
from collections import Counter
from pathlib import Path
P=Path('data/codex/astra/sweep/1055/loss1')
f=open(P/'evidence.txt','w')
for gid in [1501019,1501020,1501665]:
 g=json.loads((P/f'{gid}-trace.json').read_text());b=json.loads((P/f'{gid}-base.json').read_text());w,h=g['w'],g['h'];qu=b['queens']['us'];qe=b['queens']['them'];ours=b['ours'];foe='B' if ours=='A' else 'A'
 edges=canonical_edges(w,h,[tuple(map(int,l.split()[1:4])) for l in b['text'].splitlines() if l.startswith('EDGE ')])
 def xy(c):return (c%w,c//w)
 def view(a,c):return min(abs(a%w-c%w),w-abs(a%w-c%w))<=3 and min(abs(a//w-c//w),h-abs(a//w-c//w))<=3
 print('\nGAME',gid,w,h,file=f)
 qs=[t for t in g['turns'] if t['id']==qu]
 for t in qs[-3:]:
  state=g['full'][str(t['event'])];bodies={int(i):bb for i,bb in state['bodies'].items()};head=t['body'][0]
  print('BOARD',t['r'],'head',xy(head),'L',len(t['body']),'action',t['action'],'eats',t['eats'],file=f)
  for dy in range(-3,4):
   row=[]
   for dx in range(-3,4):
    x=(head%w+dx)%w;y=(head//w+dy)%h;c=y*w+x;ch='o' if c in state['pearls'] else '.'
    for i,bb in bodies.items():
     if c in bb:
      same=state['teams'][str(i)]==ours
      ch=('Q' if i==qu else 'M' if same else 'E') if bb[0]==c else ('q' if i==qu else 'm' if same else 'e')
    walls=''.join('NESW'[d] if edges.get(edge_id(w,h,x,y,d),(0,-1))[0]==1 else 'nesw'[d] if edges.get(edge_id(w,h,x,y,d),(0,-1))[0]==2 else '' for d in range(4))
    row.append(ch+walls)
   print(' '.join(s.ljust(6) for s in row),file=f)
  print('near',t.get('near'),file=f)
 print('queen splits',[(t['r'],len(t['body']),len(t['end'])) for t in qs if t['split']],file=f)
 print('after near',g['near_after'],file=f)
 for lo,hi in [(0,100),(101,200),(201,250),(251,300),(301,350),(351,400),(401,499)]:
  stats={}
  for s in [ours,foe]:
   ts=[t for t in g['turns'] if lo<=t['r']<=hi and t['side']==s]
   stats[s]={'turns':len(ts),'eats':dict(Counter(e[1] for t in ts for e in t['eats'])),'splits':sum(bool(t['split']) for t in ts),'stationary':sum(not t['steps'] and not t['split'] for t in ts)}
  print('ECON',lo,hi,stats,file=f)
 print('CHECKPOINT tops',[(r,g['rounds'][str(r)]) for r in [250,266,267,299,300,332,333,400,421] if str(r) in g['rounds']],file=f)
 if gid==1501020:
  hist=[]
  for t in qs:
   st=g['full'][str(t['event'])];bb=st['bodies'].get('1433',[]);n=sum(view(t['body'][0],c) for c in bb)
   if n:hist.append([t['r'],n,len(bb),view(t['body'][0],bb[0])])
  print('1433 queen-visible history',hist,file=f)
 if gid==1501665:
  for t in g['turns']:
   if 209<=t['r']<=213 and str(t['event']) in g['full']:
    st=g['full'][str(t['event'])];bb=st['bodies'].get('127',[])
    if t['side']==ours and bb and view(t['body'][0],bb[0]):print('127 SEEN BY',t['r'],t['id'],xy(t['body'][0]),file=f)
print('written',P/'evidence.txt')

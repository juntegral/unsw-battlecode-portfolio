import sys,json,ast,types
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/analysis/ladder/dossier/work']
from ladder_replay import replay,canonical_edges,edge_id
from pathlib import Path
from collections import deque,Counter,defaultdict
p=Path('data/analysis/ladder/dossier/work/tq2_near.py')
tree=ast.parse(p.read_text());tree.body=[n for n in tree.body if not isinstance(n,ast.Expr)]
m=types.ModuleType('geo_import');exec(compile(tree,str(p),'exec'),m.__dict__)
OUT=Path('data/codex/astra/sweep/0444/loss2'); F=Path('data/online/live-one1/b1488845')
for gid in (1488848,1488849):
 root=replay.load(F/f'M{gid}.replay').root();base=json.loads((OUT/f'{gid}-base.json').read_text());qids=[base['queens'][s] for s in ('us','them')]
 W,H=map(int,root.text(0).splitlines()[0].split()[1:]);bodies={};teams={};edges=[];pearls=set()
 for l in root.text(0).splitlines():
  t=l.split()
  if t[0]=='DRAGON':
   i=len(bodies);bodies[i]=deque(int(t[4+2*k])*W+int(t[3+2*k]) for k in range(int(t[2])));teams[i]=int(t[1])
  elif t[0]=='EDGE':edges.append(tuple(map(int,t[1:4])))
 geo=m.Geo(W,H,edges);rnd=-1;actor=None;turns=[];cur=None;qt=[];near=[];deaths=[];splits=[]
 def xy(c):return [c%W,c//W]
 def view(c):return {((c//W+dy)%H)*W+(c%W+dx)%W for dy in range(-3,4) for dx in range(-3,4)}
 def close():
  if cur is not None:cur['end']=list(bodies.get(actor,[]))
 def inspect():
  if qids[0] not in bodies and qids[1] in bodies:
   eh=bodies[qids[1]][0]
   for i,b in bodies.items():
    if teams[i]==0 and geo.ball(b[0]).get(eh,99)<=5:
     x=[rnd,i,len(b),xy(b[0]),len(bodies[qids[1]]),xy(eh),geo.ball(b[0])[eh]]
     if not near or near[-1]!=x:near.append(x)
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==0:close();rnd=p.i32(0);cur=None;actor=None
  elif k==1:
   close();actor=p.i32(0)
   cur=dict(r=rnd,id=actor,side=teams[actor],body=list(bodies[actor]),moves=[],eat=0,split=None,action=None)
   turns.append(cur)
   if actor in qids:
    c=bodies[actor][0];win=view(c)
    cur['context']={i:list(b) for i,b in bodies.items() if any(z in win for z in b)};cur['pearls']=sorted(pearls & win);qt.append(cur)
   if (gid==1488848 and rnd<=100 and actor==2) or (gid==1488849 and 414<=rnd<=418 and actor==787) or (gid==1488848 and 83<=rnd<=86 and actor==15):
    cur['context']={i:list(b) for i,b in bodies.items()};cur['pearls']=sorted(pearls)
  elif k==4:
   a=p.pointer(0)
   if cur is not None:cur['action']=[a.u16(0),list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []]
  elif k==3:
   pt=replay.point(p.pointer(0));c=pt[1]*W+pt[0]
   if p.u32(0):pearls.add(c)
   else:pearls.remove(c);cur['eat']+=1
  elif k==9:
   i=p.i32(0);hd=replay.point(p.pointer(0));tl=replay.point(p.pointer(1));hd=hd[1]*W+hd[0];tl=tl[1]*W+tl[0];b=bodies[i]
   if b[0]!=hd:
    if i==actor:cur['moves'].append(xy(hd))
    b.appendleft(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
   inspect()
  elif k==10:
   par,ch=p.i32(0),p.i32(4);cur['split']=ch;splits.append([rnd,par,ch])
   for j,i in enumerate((par,ch)):
    bodies[i]=deque(pt[1]*W+pt[0] for pt in map(replay.point,p.pointer(j)));teams[i]=p.u16(8)
   inspect()
  elif k==11:
   i=p.i32(0);deaths.append([rnd,i,p.u16(4),actor]);bodies.pop(i);inspect()
 close()
 lastq=[t for t in qt if t['id']==qids[0]][-3:]
 res=dict(gid=gid,w=W,h=H,queens=qids,teams=teams,lastq=lastq,near=near,splits=splits,turns=turns,deaths=deaths)
 (OUT/f'{gid}-trace.json').write_text(json.dumps(res))
 print(gid,'LASTQ',json.dumps(lastq)); print('NEAR',len(near),near[:5],near[-5:]);print('SPLITS',splits[:10])
 print('ATTACK',json.dumps([t for t in turns if (gid==1488849 and 414<=t['r']<=417 and t['id']==787) or (gid==1488848 and 83<=t['r']<=86 and t['id']==15)]))
 print('our first100 eating',[(t['r'],t['id'],t['eat'],t['split']) for t in turns if t['side']==0 and t['r']<=100 and (t['eat'] or t['split'])])
 # Compact seven-cell boards, edges represented separately as four-letter masks.
 lines=[]
 for t in lastq:
  c=t['body'][0];cx,cy=xy(c);win=view(c);occ={z:(int(i),n) for i,b in t['context'].items() for n,z in enumerate(b) if z in win};ps=set(t['pearls'])
  lines.append(f"r{t['r']} #{t['id']} L{len(t['body'])} head=({cx},{cy}); action={t['action']}; moves={t['moves']}; eats={t['eat']}")
  for dy in range(-3,4):
   row=[]
   for dx in range(-3,4):
    z=((cy+dy)%H)*W+(cx+dx)%W;v='*' if z in ps else '.'
    if z in occ:
     i,n=occ[z];v=('Q' if i==t['id'] else 'A' if teams[i]==0 else 'E') if n==0 else ('q' if i==t['id'] else 'a' if teams[i]==0 else 'e')
    row.append(v)
   lines.append(''.join(row))
  lines.append('visible heads '+str([(i,len(b),xy(b[0])) for i,b in t['context'].items() if b[0] in win]))
  lines.append('blocked edges '+str([(xy(z),''.join('NESW'[d] for d in range(4) if geo.nxt[z][d]<0)) for z in sorted(win) if any(x<0 for x in geo.nxt[z])]))
  lines.append('')
 (OUT/f'{gid}-boards.txt').write_text('\n'.join(lines))

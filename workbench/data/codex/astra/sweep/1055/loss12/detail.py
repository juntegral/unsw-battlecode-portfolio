import sys,json,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('geo',Path.cwd()/'data/analysis/ladder/losses/counts/count_replays.py');gm=importlib.util.module_from_spec(spec);spec.loader.exec_module(gm)
for gid in (1504482,1504484,1504486):
 if not (P/f'{gid}-base.json').exists():continue
 b=json.loads((P/f'{gid}-base.json').read_text());ts=json.loads((P/f'{gid}-turns.json').read_text());s=json.loads((P/f'{gid}-summary.json').read_text());text=b['text'];w,h=map(int,text.splitlines()[0].split()[1:3]);edges=[tuple(map(int,l.split()[1:4])) for l in text.splitlines() if l.startswith('EDGE ')];g=gm.Geometry(w,h,edges);teams={}
 for t in ts:teams[t['id']]=t['side']
 xy=lambda c:(c%w,c//w)
 lines=[f'{gid} {b["map"]} {w}x{h}']
 qid=b['queens']['us'];qts=[t for t in ts if t['id']==qid];qd=next((d for d in b['deaths'] if d['id']==qid),None)
 for t in qts[-3:]:
  lines.append(str({k:v for k,v in t.items() if k not in ('bodies','pearls')}));lines.append(f'head {xy(t["head"])}; moves {[xy(c) for c in t["steps"]]}')
  bodies={int(i):bb for i,bb in t['bodies'].items()};occ={c:(i,k) for i,bb in bodies.items() for k,c in enumerate(bb)};hx,hy=xy(t['head']);near=[];grid=[];walls=[]
  for dy in range(-3,4):
   row=[]
   for dx in range(-3,4):
    x,y=(hx+dx)%w,(hy+dy)%h;c=y*w+x
    if c in occ:
     i,k=occ[c];ch=('Q' if i==qid else 'A' if teams[i]==0 else 'E') if k==0 else ('q' if i==qid else 'a' if teams[i]==0 else 'e')
     if k==0:near.append([i,xy(c),len(bodies[i])])
    else:ch='*' if c in t['pearls'] else '.'
    row.append(ch)
    for d,(kind,dest) in enumerate(g.moves[c]):
     if kind==1:walls.append([xy(c),'NESW'[d]])
   grid.append(''.join(row))
  lines+=grid;lines.append('heads '+str(near));lines.append('kelp '+str(walls))
  if qd:
   aid=qd['actor'];ab=bodies.get(aid,[]);lines.append('attacker '+str([aid,[xy(c) for c in ab],sum(g.visible(t['head'],c) for c in ab)]));
   att=next((z for z in ts if z['id']==aid and z['r']==qd['round']),None)
   if att:lines.append('attacker turn '+str(att));lines.append('attack pearls already present '+str([(xy(c),c in t['pearls']) for c in att['steps']]))
 lines.append('queen splits '+str([x for x in s['queen_splits'] if x['parent']==qid]));lines.append('queen growth '+str([(t['r'],t['L'],t['eaten'],t['endL']) for t in qts if t['eaten'] or t['L']!=t['endL']]))
 lines.append('late deaths '+str(s['late_long_deaths']))
 (P/f'{gid}-detail.txt').write_text('\n'.join(lines)+'\n')
 print('\n'.join(lines[:40]))

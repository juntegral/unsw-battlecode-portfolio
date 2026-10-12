import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import deque,Counter
import evidence as e
O=e.O
labels={}
for mp in Path('data/online/smoke').glob('one8-*-old/game-*.json'):labels[json.loads(mp.read_text())['id']]=mp.parent.name
rows=json.loads((O/'recurrence.json').read_text())
for r in rows:r['label']=labels.get(r['id'],'ranked')
(O/'recurrence.json').write_text(json.dumps(rows,indent=2))
results={}
for gid in (1485486,1485489,1485490):
 g=json.loads((O/f'M{gid}.json').read_text());d=g['detail'];root,edge,step=e.geo(g);q=d['queens'][0];t=d['qt'][0][-1]
 if gid==1485489:t=d['qt'][0][-3]
 ctx={int(i):list(map(tuple,b)) for i,b in t['context'].items()};head=tuple(t['body'][0]);w,H=d['w'],d['h']
 def bfs(start,end,blocked,limit):
  seen={start};queue=deque([(start,[])])
  while queue:
   c,p=queue.popleft()
   if c==end:return p
   if len(p)>=limit:continue
   for k in range(4):
    nxt=step(c,k)
    if nxt is None or nxt in seen or (nxt in blocked and nxt!=end):continue
    seen.add(nxt);queue.append((nxt,p+[k]))
  return None
 out={'final_replay_stats':[]}
 for s in (0,1):
  raw=root.pointer(4).pointer(d['own'] if s==0 else 1-d['own']);final=d['snaps'][str(max(map(int,d['snaps'])))][s]
  measured=tuple(raw.i32(x) for x in (0,4,8,12));assert measured==tuple(final[k] for k in (3,1,2,0));out['final_replay_stats'].append(measured)
 if gid!=1485489:
  death=next(x for x in d['deaths'] if x['id']==q);aid=death['actor'];start=ctx[aid][0];end=tuple(death['body'][0]);allvis={c for b in ctx.values() for c in b if e.visible(c,head,w,H)}
  oldq=list(map(tuple,t['body']));staticblocked=allvis-{oldq[-1]};newq=list(map(tuple,t['end']));dynamicblocked=(allvis-set(oldq))|set(newq)
  out.update(start=start,end=end,visible=sum(e.visible(c,head,w,H) for c in ctx[aid]),full_length=len(ctx[aid]),static_target_blocked=end in staticblocked,dynamic_path=bfs(start,end,dynamicblocked,3),old_release=len(oldq)-oldq.index(end)+1 if end in oldq else 0)
  if gid==1485486:alt=[(40,12)]+oldq[:-1]
  else:alt=[(46,1)]+oldq[:-1]
  out['alternative_head']=alt[0];out['alternative_first_step']=[k for k in range(4) if step(head,k)==alt[0]]
  out['alternative_unoccupied']=alt[0] not in allvis
  out['alternative_attack_within3']=bfs(start,alt[0],(allvis-set(oldq))|set(alt),3)
 else:
  dest=(27,13);partner=(26,13)
  out['portal_other_edge_seen']=any(e.visible(dest,z['body'][0],w,H) or e.visible(partner,z['body'][0],w,H) for z in d['qt'][0] if z['r']<=111)
  out['north_exit']=step(head,0);out['north_occupied']=out['north_exit'] in {c for b in ctx.values() for c in b}
  out['dest_exits']=[(k,step(dest,k)) for k in range(4) if step(dest,k) is not None]
  seen={head};queue=deque([head])
  while queue:
   c=queue.popleft()
   for k in range(4):
    if edge(c,k)[0]!=0:continue
    nxt=step(c,k)
    if nxt not in seen:seen.add(nxt);queue.append(nxt)
  out['open_component']=len(seen);out['cells']=w*H
 results[str(gid)]=out
print(json.dumps(results,indent=2));(O/'verification.json').write_text(json.dumps(results,indent=2))
summary=[]
for lab in sorted(set(r['label'] for r in rows)):
 rr=[r for r in rows if r['label']==lab]
 summary.append(dict(label=lab,games=len(rr),queen_rammed=sum(r.get('ram',False) for r in rr),truncated_nonpearl=sum(r.get('truncated_short',False) and r['eat']==0 for r in rr),release=sum(r.get('body_release',False) for r in rr),portal_wall=sum(r.get('recent_portal',False) for r in rr)))
(O/'summary.json').write_text(json.dumps(summary,indent=2))
for r in rows:
 g=json.loads((O/f"M{r['id']}.json").read_text());d=g['detail'];m=g['meta'];final=d['snaps'][str(max(map(int,d['snaps'])))];assert final[0][2]==m['scores'+'AB'[d['own']]];assert final[1][2]==m['scores'+'AB'[1-d['own']]]
print('metadata final totals verified',len(rows))

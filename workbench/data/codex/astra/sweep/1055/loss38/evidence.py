import json,sys
sys.dont_write_bytecode=True
sys.path.insert(0,'tools')
from ladder_replay import canonical_edges,edge_id
from pathlib import Path
from collections import deque,defaultdict,Counter
P=Path(__file__).parent
out={};boards=[]
for gid in [1515669,1515670,1506911]:
 s=json.loads((P/f'{gid}-scan.json').read_text());t=json.loads((P/f'{gid}-trace.json').read_text());w,h=t['size'];raw=[]
 for line in s['text'].splitlines():
  q=line.split()
  if q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
 edges=canonical_edges(w,h,raw);portals=defaultdict(list)
 for e,(k,pid) in edges.items():
  if k==2:portals[pid].append(e)
 def dest(a,d):
  e=edge_id(w,h,*a,d);k,pid=edges.get(e,(0,-1))
  if k==1:return None
  if k==2:
   z=next(z for z in portals[pid] if z!=e);row,x=divmod(z,w+1)
   return ((x-(d==3))%w,(row//2-(d==0))%h)
  dx,dy=[(0,-1),(1,0),(0,1),(-1,0)][d];return ((a[0]+dx)%w,(a[1]+dy)%h)
 reverse=defaultdict(list)
 for x in range(w):
  for y in range(h):
   for d in range(4):
    b=dest((x,y),d)
    if b is not None:reverse[b].append((x,y))
 cache={}
 def distance(a,b):
  b=tuple(b)
  if b not in cache:
   ds={b:0};q=deque([b])
   while q:
    c=q.popleft()
    for n in reverse[c]:
     if n not in ds:ds[n]=ds[c]+1;q.append(n)
   cache[b]=ds
  return cache[b].get(tuple(a),99999)
 close=[[r,i,distance(a,b),a,b] for r,i,_,a,b in t['distances']]
 own=0 if s['ours']=='A' else 1;qid=t['queens'][0]
 moves=[]
 for turn in t['turns']:
  a=turn['body'][0]
  for d,b in zip(turn['dirs'],turn['moves']):
   assert dest(tuple(a),d)==tuple(b),(gid,turn['r'],turn['id'],a,d,b)
   if edges.get(edge_id(w,h,*a,d),(0,0))[0]==2:moves.append([turn['r'],turn['id'],turn['side'],a,b])
   a=b
 heads={};side={};qown,qenemy=t['queens'];best_geo=None;best_graph=None
 for line in s['text'].splitlines():
  z=line.split()
  if z[0]=='DRAGON':
   i=len(heads);heads[i]=(int(z[3]),int(z[4]));side[i]=int(z[1])
 def observe(r):
  global best_geo,best_graph
  if qown in heads or qenemy not in heads:return
  b=heads[qenemy]
  for i,a in heads.items():
   if side[i]!=own:continue
   dx=abs(a[0]-b[0]);dy=abs(a[1]-b[1]);g=min(dx,w-dx)+min(dy,h-dy);d=distance(a,b)
   if best_geo is None or g<best_geo[2]:best_geo=[r,i,g,a,b]
   if best_graph is None or d<best_graph[2]:best_graph=[r,i,d,a,b]
 for turn in t['turns']:
  i=turn['id'];side[i]=turn['side'];heads[i]=tuple(turn['body'][0]);observe(turn['r'])
  for b in turn['moves']:heads[i]=tuple(b);observe(turn['r'])
  if turn['split']:
   child=turn['split'][1];side[child]=side[i];heads[child]=tuple(turn['body'][-1]);observe(turn['r'])
  for dead,_,_ in turn['deaths']:heads.pop(dead,None);observe(turn['r'])
  if turn['end']:heads[i]=tuple(turn['end'][0])
 out[str(gid)]={'all_events_min_manhattan':best_geo,'all_events_min_topological':best_graph,'closest_topological_own_turns':sorted(close,key=lambda z:z[2])[:5], 'first_within5':next((z for z in close if z[2]<=5),None),'turns_within5':sum(z[2]<=5 for z in close),'portal_crossings_first100':[z for z in moves if z[0]<=100], 'our_turns_first100':sum(x['side']==own and x['r']<=100 for x in t['turns']), 'our_eating_turns_first100':sum(x['side']==own and x['r']<=100 and bool(x['eat']) for x in t['turns'])}
 death=next(d for d in s['deaths'] if d['id']==qid)
 boards.append(f'| {gid} | 여왕 #{qid}: 마지막 세 자기 턴 직전 [M] |')
 for x in [x for x in t['queen_pre'] if x['id']==qid and x['r']<=death['round']][-3:]:
  body=x['bodies'][str(qid)];grid='<br>'.join(' '.join(row) for row in x['board'])
  boards.append(f"| r{x['r']}, 중심 {tuple(body[0])} | <pre>{grid}</pre> |")
 if gid==1515669:
  for r in (25,50,100):
   ts=[z for z in t['turns'] if z['side']==own and z['r']<=r]
   print(gid,r,'heads',Counter(tuple(z['body'][0]) for z in ts).most_common(8))
 print(gid,json.dumps(out[str(gid)],ensure_ascii=False))
(P/'evidence.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
(P/'boards.txt').write_text('\n'.join(boards))

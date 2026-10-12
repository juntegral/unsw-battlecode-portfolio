import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter,deque,defaultdict
import analyze
lr=analyze.shared.lr
O=analyze.OUT
TARGETS=(1485486,1485489,1485490)
def visible(c,h,w,H):return min(abs(c[0]-h[0]),w-abs(c[0]-h[0]))<=3 and min(abs(c[1]-h[1]),H-abs(c[1]-h[1]))<=3
def geo(g):
 root=lr.replay.load(Path(g['path'])).root();d=g['detail'];w,H=d['w'],d['h']
 raw=[tuple(map(int,x.split()[1:4])) for x in root.text(0).splitlines() if x.startswith('EDGE ')];edges=lr.canonical_edges(w,H,raw);portals=defaultdict(list)
 for e,(k,p) in edges.items():
  if k==2:portals[p].append(e)
 def edge(c,k):return edges.get(lr.edge_id(w,H,*c,k),(0,-1))
 def step(c,k):
  kind,p=edge(c,k)
  if kind==1:return None
  if kind==2:
   e=lr.edge_id(w,H,*c,k);other=next(e2 for e2 in portals[p] if e2!=e);row,x=divmod(other,w+1);return ((x-(k==3))%w,(row//2-(k==0))%H)
  dx,dy=((0,-1),(1,0),(0,1),(-1,0))[k];return ((c[0]+dx)%w,(c[1]+dy)%H)
 return root,edge,step

def classify(g):
 d=g['detail'];q=d['queens'][0];death=next((x for x in d['deaths'] if x['id']==q),None)
 row=dict(id=d['gid'],map=d['map'],label=Path(g['path']).parent.name,queen_death=death and death['reason'],r=death and death['r'])
 if not death:return row
 t=d['qt'][0][-1];a=str(death['actor']);w,H=d['w'],d['h'];b=t['context'].get(a)
 if death['reason']==3 and death['actor']!=q and b:
  head=t['body'][0];seen=sum(visible(c,head,w,H) for c in b)
  hv=visible(b[0],head,w,H);old=next((i for i,c in enumerate(t['body']) if c==death['body'][0]),None)
  memory=max([sum(visible(c,z['body'][0],w,H) for c in z['context'].get(a,[])) for z in d['qt'][0] if z['r']<=t['r']],default=0)
  size=max(seen+1,3,memory) if seen<len(b) else max(seen,memory)
  reach=max((max(seen,memory)+3)//4,min((size+3)//4+size-2,3))
  row.update(ram=True,visible=hv,seen=seen,true_length=len(b),memory_max=memory,old_body_offset=old,old_release=len(t['body'])-old+1 if old is not None else None,steps=death['step'],eat=next(z['eat'] for z in d['turns'] if z['id']==death['actor'] and z['r']==death['r']),start=b[0],end=death['body'][0],truncated_short=hv and seen<len(b) and death['step']>reach,body_release=hv and old is not None and old>0 and len(t['body'])-old+1>2,estimated_reach_upper=reach)
 if death['reason']==0:
  root,edge,step=geo(g)
  row['recent_portal']=any(edge(tuple(z['body'][0]),z['dirs'][0])[0]==2 for z in d['qt'][0][-4:] if z['dirs'])
 return row

def main():
 games=[]
 for p in sorted(O.glob('M*.json')):
  g=json.loads(p.read_text());d=g['detail']
  if d['bots'][d['own']]!='21126':continue
  games.append(g)
 rows=[classify(g) for g in games]
 (O/'recurrence.json').write_text(json.dumps(rows,indent=2))
 print('N',len(rows),'groups',dict(Counter(r['label'] for r in rows)))
 for key in ('ram','truncated_short','body_release','recent_portal'):
  vals=[r for r in rows if r.get(key)];print(key,len(vals),[(r['id'],r['r'],r.get('steps')) for r in vals])
 f=open(O/'boards.md','w');print('[M] 마지막 세 여왕 차례 시작 판면. Q/q 여왕 머리/몸, A/a 아군, E/e 적; 벽 ─│, 포털 P. 좌표는 0부터, 진주 생략.\n',file=f)
 check=open(O/'checkpoints.md','w');print('[M] 각 라운드 종료: 머릿수/총길이/최장/여왕. 우리 : 상대.\n\n|r|1485486|1485489|1485490|\n|---|---|---|---|',file=check)
 for r in list(range(0,500,25))+[499]:
  vals=[]
  for gid in TARGETS:
   d=next(g['detail'] for g in games if g['detail']['gid']==gid);sn=d['snaps'][str(r)];vals.append(' : '.join('/'.join(str(s[k]) for k in (3,2,1,0)) for s in sn))
  print('|'+str(r)+'|'+'|'.join(vals)+'|',file=check)
 check.close()
 for g in games:
  d=g['detail'];gid=d['gid']
  if gid not in TARGETS:continue
  root,edge,step=geo(g);w,H=d['w'],d['h']
  last=max(int(r) for r in d['snaps'] if d['snaps'][r][0][:3]>=d['snaps'][r][1][:3]);print('TURN',gid,last+1)
  for t in d['qt'][0][-3:]:
   x,y=t['body'][0];occ={}
   for i,b in t['context'].items():
    char='Q' if int(i)==d['queens'][0] else 'A' if d['teams'][i]==0 else 'E'
    for k,c in enumerate(b):occ[tuple(c)]=char if k==0 else char.lower()
   print(f"\n### [M] {gid} r{t['r']} L{t['L']}; 머리 ({x},{y}); 명령 {t['dirs'] if t['action']==0 else '분열'}\n\nx={(x-3)%w}…{(x+3)%w}, y={(y-3)%H}…{(y+3)%H}; N/E/S/W=0/1/2/3\n```",file=f)
   for yy in range(y-3,y+4):
    print(''.join('+'+('──' if edge((xx%w,yy%H),0)[0]==1 else 'PP' if edge((xx%w,yy%H),0)[0]==2 else '  ') for xx in range(x-3,x+4))+'+',file=f)
    print(''.join(('│' if edge((xx%w,yy%H),3)[0]==1 else 'P' if edge((xx%w,yy%H),3)[0]==2 else ' ')+occ.get((xx%w,yy%H),'.')+' ' for xx in range(x-3,x+4)),file=f)
   print('```\n[M] 실제 경로: '+str(t['steps'])+'; 종료 길이 '+str(len(t['end'])),file=f)
   if gid==1485489:
    print('PORTAL',t['r'],'neighbors',[(k,step((x,y),k),[(i,b.index(list(step((x,y),k)))) for i,b in t['context'].items() if step((x,y),k) is not None and list(step((x,y),k)) in b]) for k in range(4)])
  if gid==1485489:
   z=d['qt'][0][-3];dest=(27,13)
   print('portal dest previous seen',[(t['r'],t['body'][0]) for t in d['qt'][0] if t['r']<111 and visible(dest,t['body'][0],w,H)])
   print('portal pre turns',[(t['r'],t['L'],t['body'][0],t['steps'],t['action']) for t in d['qt'][0][-9:]])
 f.close()

if __name__=="__main__":main()

import sys
sys.dont_write_bytecode=True
import json,re,hashlib
from pathlib import Path
from collections import deque,Counter,defaultdict
from datetime import datetime
sys.path[:0]=['tools','data/analysis/ladder/dossier/work','data/analysis/ladder/dossier/online']
from lineage import major_lineage
import o1_scan
import label_report
from ladder_replay import replay
OUT=Path('data/codex/astra/longest')
BOTS={'20850':'one1','20880':'one2','20910':'one3','20941':'one4','20980':'one5'}

def detail(path,j,base):
 root=replay.load(path).root(); lines=root.text(0).splitlines(); W,H=map(int,lines[0].split()[1:3]); own=int(j['teamAId']!=1119)
 bodies={}; teams={}; stats={}; eats=[]; deaths=[]; present={}; expected=0; source=None; snaps={}; cohort={}; firstphase=None; logs=[]
 def init(i,side,L,parent=None):
  teams[i]=side; stats[i]=dict(id=i,side=side,born=rnd,start=L,parent=parent,natural=0,own_drop=0,foe_drop=0,stop_drop=0,feed_sources=[],splits=[],death=None,lineage=[])
 rnd=-1
 for line in lines:
  q=line.split()
  if q and q[0]=='DRAGON':
   i=len(bodies); bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2]))); init(i,int(int(q[1])!=own),len(bodies[i]))
 queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
 def gap(a,b):
  dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1]); return min(dx,W-dx)+min(dy,H-dy)
 def top(s): return max((i for i in bodies if teams[i]==s),key=lambda i:(len(bodies[i]),-i),default=None)
 def sample():
  result=[]
  for s in (0,1):
   i=top(s); st=stats.get(i,{})
   result.append(dict(id=i,length=len(bodies[i]) if i is not None else 0,role='queen' if i==queens[s] else 'fed' if st.get('stop_drop',0)>0 else 'inherited-fed' if any(x['stop_drop']>0 for x in major_lineage(st.get('lineage',[]))) else 'ordinary',natural=st.get('natural',0),own_drop=st.get('own_drop',0),foe_drop=st.get('foe_drop',0),stop_drop=st.get('stop_drop',0),alive=sum(teams[z]==s for z in bodies),total=sum(len(b) for z,b in bodies.items() if teams[z]==s)))
  if rnd>=200 and (rnd%25==0 or rnd==base['last']): snaps[rnd]=result
  if rnd==400:
   lead=top(0)
   if lead is not None:
    for z,b in bodies.items():
     if teams[z]==0 and z!=lead:
      cohort[z]=dict(id=z,length=len(b),leader=lead,distance=gap(b[0],bodies[lead][0]),eligible=len(b)*2<=len(bodies[lead]) and z!=queens[0],arrived=None,stop=None,death=None)
 def arrival():
  lead=top(0)
  if rnd<=400 or lead is None:return
  for z,c in cohort.items():
   if z in bodies and z!=lead and c['arrived'] is None and len(bodies[z])*2<=len(bodies[lead]) and gap(bodies[z][0],bodies[lead][0])<=3:
    c['arrived']=[rnd,lead]
 actor=None; deathn=0; action=None
 for ev in root.pointer(3):
  k=ev.u16(0); p=ev.pointer(0)
  if k==0:
   if rnd>=0:sample()
   rnd=p.i32(0); actor=None
  elif k==1:
   actor=p.i32(0); action=None; arrival()
   cap=200 if base['bot'] in ('20850','20880') else 350
   if actor in bodies and teams[actor]==0 and firstphase is None and (rnd>400 or rnd>cap and sum(teams[z]==0 for z in bodies)>=56):firstphase=rnd
  elif k==4:
   a=p.pointer(0); used=p.pointer(1); action=dict(kind=a.u16(0) if a else None,moves=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else [],timeout=p.bit(32) or bool(used and used.bit(64)))
  elif k==6:
   logs.append([rnd,actor,p.text(0)])
  elif k==3:
   cell=replay.point(p.pointer(0))
   if p.u32(0):
    present[cell]=source if expected else None
    if expected:expected-=1
   else:
    src=present.pop(cell); st=stats[actor]; typ='natural' if src is None else 'own_drop' if src['side']==teams[actor] else 'foe_drop'; st[typ]+=1
    e=dict(round=rnd,id=actor,side=teams[actor],origin=typ,source=src['id'] if src else None,death_round=src['round'] if src else None,stop=src['cause']=='stop' if src else False)
    eats.append(e)
    if src:
     src['eaters'].append([rnd,actor])
     if src['side']==teams[actor] and src['cause']=='stop':
      st['stop_drop']+=1
      if src['id'] not in st['feed_sources']:st['feed_sources'].append(src['id'])
  elif k==9:
   i=p.i32(0); hd,tl=replay.point(p.pointer(0)),replay.point(p.pointer(1)); b=bodies[i]
   if b[0]!=hd:b.appendleft(hd)
   while len(b)>1 and b[-1]!=tl:b.pop()
   assert b[-1]==tl
  elif k==10:
   parent,child=p.i32(0),p.i32(4); before=len(bodies[parent])
   for z,i in enumerate((parent,child)):bodies[i]=deque(replay.point(c) for c in p.pointer(z))
   init(child,teams[parent],len(bodies[child]),parent); stats[child]['lineage']=stats[parent]['lineage']+[dict(id=parent,round=rnd,before=before,child_length=len(bodies[child]),**{k:stats[parent][k] for k in ('natural','own_drop','foe_drop','stop_drop')})]; stats[parent]['splits'].append([rnd,before,len(bodies[parent]),child])
  elif k==11:
   i=p.i32(0); b=bodies[i]; old=base['deaths'][deathn]; deathn+=1
   assert [rnd,teams[i],len(b)]==old[:3]
   longer=[z for z in bodies if z!=i and teams[z]==teams[i] and len(bodies[z])>len(b)]
   near=sorted([[z,len(bodies[z]),gap(b[0],bodies[z][0])] for z in longer],key=lambda x:(x[2],-x[1],x[0]))
   topid=top(teams[i]); src=dict(id=i,side=teams[i],round=rnd,length=len(b),cause=old[4],reason=p.u16(4),actor=actor,top=topid==i,top_id=topid,top_distance=old[16],free=old[5],action=action,nearest_longer=near[0] if near else None,near_longer=[z for z,L,d in near if d<=3],eaters=[])
   deaths.append(src);stats[i]['death']=dict(round=rnd,cause=old[4],length=len(b),actor=actor)
   if i in cohort:cohort[i]['death']=stats[i]['death'];cohort[i]['stop']=rnd if old[4]=='stop' else None
   source=src;expected=(len(b)+1)//2;bodies.pop(i)
 if rnd>=0:sample()
 assert deathn==len(base['deaths'])
 for s in (0,1):
  assert snaps[rnd][s]['total']==base['ends'][s][1]
  assert sum(e['side']==s for e in eats)==sum(e[1]==s for e in base['eats'])
 leaders=set(v['id'] for snap in snaps.values() for v in snap if v['id'] is not None)
 for s in (0,1):leaders.add(queens[s])
 return dict(gid=j['id'],path=str(path),label=base['src'],bot=base['bot'],map=base['map'],opp=base['opp'],result=base['result'],how=base['how'],last=rnd,queens=queens,snapshots=snaps,leaders={i:stats[i] for i in sorted(leaders)},deaths=deaths,eats=eats,cohort400=list(cohort.values()),phase_nonqueen=firstphase,logs=logs,all_dragons=stats,schema=2)

def main():
 jobs=[]; inventory=[]; seen=set()
 previous={c['gid']:c for c in json.loads((OUT/'census.json').read_text())} if (OUT/'census.json').exists() else {}
 for v in range(1,6):
  for opp in (('w1','d1','c1') if v==5 else ('w1','d1')):
   if v==2 and opp=='d1':continue
   label=f'one{v}-{opp}'; inv=label_report.inventory(label,'old');inventory.append(dict(label=label,available=len(inv['jobs']),planned=inv['planned'],notes=inv['notes']))
   for p,j in inv['jobs']:
    if j['id'] not in seen:jobs.append((label,p,j));seen.add(j['id'])
 for label,p,j in o1_scan.jobs('live'):
  if j['id'] in seen:continue
  if j['id'] in previous:bot=previous[j['id']]['bot']
  else:
   r=replay.load(p).root();bot=[r.text(1),r.text(2)][int(j['teamAId']!=1119)]
  if bot in BOTS:jobs.append((BOTS[bot]+'-ranked',p,j));seen.add(j['id'])
 (OUT/'inventory.json').write_text(json.dumps(dict(time=datetime.now().astimezone().isoformat(),sets=inventory,total=len(jobs)),ensure_ascii=False,indent=2))
 cachep=OUT/'base.jsonl';cache={}
 if cachep.exists():
  for line in cachep.read_text().splitlines():
   b=json.loads(line);cache[b['gid']]=b
 selected=[]; census=[]
 with cachep.open('a') as f:
  for n,(label,p,j) in enumerate(jobs):
   if j['id'] in previous:
    census.append(previous[j['id']]);how=census[-1]['how']
   else:
    r=replay.load(p).root(); fin=r.pointer(4); st=[fin.pointer(z) for z in (0,1)]; own=int(j['teamAId']!=1119); bot=[r.text(1),r.text(2)][own]
    how='elim' if any(z.i32(0)==0 for z in st) else 'queen' if st[0].i32(12)!=st[1].i32(12) else 'longest' if st[0].i32(4)!=st[1].i32(4) else 'total'
    census.append(dict(gid=j['id'],label=label,bot=bot,path=str(p),how=how,result='draw' if fin.u16(4)!=1 else 'win' if fin.u16(6)==own else 'loss'))
   if how!='longest':continue
   b=cache.get(j['id'])
   if b is None:
    b=o1_scan.scan(label,p,j); f.write(json.dumps(b,separators=(',',':'))+'\n');f.flush()
   if b['how']=='longest':selected.append((p,j,b))
   print(f"online {n+1}/{len(jobs)} {j['id']} {b['how']}",flush=True)
 (OUT/'census.json').write_text(json.dumps(census,indent=2))
 dc={g['gid']:g for g in map(json.loads,(OUT/'games.jsonl').read_text().splitlines())} if (OUT/'games.jsonl').exists() else {}
 with (OUT/'games.jsonl').open('w') as f:
  for n,(p,j,b) in enumerate(selected):
   g=dc.get(j['id']);g=g if g and g.get('schema')==2 else detail(p,j,b);f.write(json.dumps(g,separators=(',',':'))+'\n');f.flush();print('detail',n+1,len(selected),j['id'],flush=True)
 lc={(g['label'],g['gid']):g for g in map(json.loads,(OUT/'local.jsonl').read_text().splitlines())} if (OUT/'local.jsonl').exists() else {}
 with (OUT/'local.jsonl').open('w') as f:
  for arm in ('mArl_vh','mAl4_vh'):
   for folder in sorted((Path.home()/'meow-redteam/solo/runs'/arm).glob('*-seed*-side*')):
    if not (folder/'result.txt').exists() or not (folder/'game.replay').exists():continue
    match=re.fullmatch(r'(.+)-seed(\d+)-side(\d)',folder.name);side=int(match[3]);j=dict(id=folder.name,teamAId=1119 if side==0 else 1,teamBId=1 if side==0 else 1119,mapName=match[1],teamAName='A',teamBName='B')
    g=lc.get((arm,j['id']))
    if g is None or g.get('schema')!=2:
     b=o1_scan.scan(arm,folder/'game.replay',j);g=detail(folder/'game.replay',j,b);g['base']=b
    f.write(json.dumps(g,separators=(',',':'))+'\n');f.flush();print('local',arm,folder.name,flush=True)
if __name__=='__main__':main()

import sys
sys.dont_write_bytecode=True
import json,collections,datetime,statistics
from pathlib import Path
sys.path.insert(0,'data/analysis/ladder/dossier/work')
sys.path.insert(0,'tools')
import o1_scan
import ladder_replay as lr
OUT=Path('data/codex/astra/band')
CUT='2026-10-08T18:09:00'
TARGETS=('preyas','computers','codehammer','adrak','acegi','cache me','wehavequizzes')

def inventory():
 seen={}; rejected=[]; copies=0
 folders=list(Path('data/online/smoke').glob('*-old'))+list(Path('data/online/live-one1').glob('b*'))
 for folder in sorted(folders):
  for mp in sorted(folder.glob('game-*.json')):
   j=json.loads(mp.read_text())
   if 1119 not in (j.get('teamAId'),j.get('teamBId')):continue
   own=0 if j['teamAId']==1119 else 1
   opp=j['team'+'AB'[1-own]+'Name']
   if not any(t in opp.lower() for t in TARGETS):continue
   if j.get('startedAt','')<CUT:continue
   gid=j['id']; rp=folder/f'M{gid}.replay'
   if gid in seen: copies+=1;seen[gid]['copies'].append(str(rp));continue
   if not rp.exists():rejected.append([gid,'missing replay']);continue
   root=lr.replay.load(rp).root();bot=root.text(own+1)
   if not bot.isdigit() or int(bot)<21126:rejected.append([gid,'old bot',bot]);continue
   seen[gid]=dict(path=str(rp),meta=j,bot=bot,opponent_bot=root.text(2-own),copies=[])
 doc=dict(cutoff=CUT+'Z',collected=datetime.datetime.now().astimezone().isoformat(),count=len(seen),duplicates=copies,rejected=rejected,games=list(seen.values()))
 (OUT/'inventory.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2))
 return doc['games']

def analyze(job):
 path=Path(job['path']);j=job['meta'];g=o1_scan.scan(path.parent.name,path,j)
 x=lr.scan(path,j,path.parent.name,set())
 assert g['ends']==[g['snaps'][str(g['last'])][s] for s in (0,1)]
 for s,name in enumerate(('us','them')):
  assert g['ends'][s][:4]==[x['final'][name][k] for k in ('alive','total','longest','queen_length')]
 root=lr.replay.load(path).root();own=0 if j['teamAId']==1119 else 1
 teams={};rnd=-1;turns=[0,0]
 for line in root.text(0).splitlines():
  q=line.split()
  if q and q[0]=='DRAGON':teams[len(teams)]=int(int(q[1])!=own)
 for ev in root.pointer(3):
  k=ev.u16(0)
  if k==1:turns[teams[ev.pointer(0).i32(0)]]+=1
  elif k==10:
   p=ev.pointer(0);teams[p.i32(4)]=int(p.u16(8)!=own)
 # Last round whose lexicographic game score is not strictly opponent-leading.
 def cmp(st):
  a,b=st['us'],st['them']
  if a['alive']==0 or b['alive']==0:return (a['alive']>0)-(b['alive']>0)
  A=tuple(a[k] for k in ('queen_length','longest','total'));B=tuple(b[k] for k in ('queen_length','longest','total'))
  return (A>B)-(A<B)
 rounds=sorted(x['snapshots']);last_nonloss=max((r for r in rounds if cmp(x['snapshots'][r])>=0),default=-1)
 turn=next((r for r in rounds if r>last_nonloss),None) if g['result']=='loss' else None
 qfeeds=[]
 for p in x['pearls']:
  if p['eater']=='them' and p['eater_id']==x['queens']['them']:
   qfeeds.append({k:p[k] for k in ('dragon','drop_side','drop_round','eat_round','wait','death')})
 deaths={d['death']:d for d in x['deaths']}
 for p in qfeeds:
  d=deaths[p['death']];p.update(cause=d['cause'],length=d['length'],other=d['other'])
 # Snapshot ledger conservation checks for every 25-round interval.
 residual=[]
 for a,b in zip(sorted(map(int,g['snaps'])),sorted(map(int,g['snaps']))[1:]):
  for s in (0,1):
   eat=sum(a<e[0]<=b and e[1]==s for e in g['eats'])
   dead=sum(d[2] for d in g['deaths'] if a<d[0]<=b and d[1]==s)
   paid=sum(p[3] for p in g['paids'] if a<p[0]<=b and p[1]==s)
   r=g['snaps'][str(b)][s][1]-g['snaps'][str(a)][s][1]-eat+dead+paid
   if r:residual.append([a,b,s,r])
 g.update(turns=turns,turn_round=turn,opponent_bot=job['opponent_bot'],ranked=j['ranked'],start=j['startedAt'],path=str(path),
  qfeeds=qfeeds,queen_ids=x['queens'],queen_deaths=[{k:d[k] for k in ('id','side','round','length','cause','reason','actor','other')} for d in x['deaths'] if d['id'] in x['queens'].values()],
  audit=dict(anomalies=x['anomalies'],residual=residual,final_match=True),
  snapshots=x['snapshots'])
 return g

if __name__=='__main__':
 jobs=json.loads((OUT/'inventory.json').read_text())['games'] if (OUT/'inventory.json').exists() else inventory();print('inventory',len(jobs),flush=True)
 done={}
 cache=OUT/'games.jsonl'
 if cache.exists():
  done={g['gid']:g for g in map(json.loads,cache.read_text().splitlines())}
 with cache.open('a') as f:
  for n,job in enumerate(jobs):
   if job['meta']['id'] in done:continue
   original_load=lr.replay.load
   cached=original_load(Path(job['path']))
   lr.replay.load=lambda path: cached
   try: g=analyze(job)
   finally: lr.replay.load=original_load
   del cached
   f.write(json.dumps(g,ensure_ascii=False,separators=(',',':'))+'\n');f.flush()
   print(n+1,g['gid'],g['opp'],g['bot'],g['result'],g['how'],'audit',g['audit'],flush=True)

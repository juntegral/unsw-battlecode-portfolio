import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib
from collections import Counter
from datetime import datetime
sys.path.insert(0,'data/codex/astra/weak')
import analyze as prior
from moments import audit,Board
OUT=Path(__file__).resolve().parent

def indicators(d,B,own):
 t=d['last'];a=d['attacker']
 if d['reason']!=3 or a['id']==d['id'] or t is None:return None
 bodies={int(i):[tuple(c) for c in b] for i,b in t['bodies'].items()};teams={int(i):s for i,s in t['teams'].items()}
 h=tuple(t['h']);end=tuple(t['end']) if t['end'] else tuple(d['h']);vis=t['visible'];occ={c for b in bodies.values() for c in b}
 enemy=[i for i in vis if teams[i]!=own];ally=[i for i in vis if teams[i]==own]
 # Frozen bodies, free geometric reach only; no future opponent movement or growth assumed.
 reached=set()
 for i in enemy:
  reached.update(c for c,dist in B.flood(bodies[i][0],(len(bodies[i])+3)//4,occ).items() if dist>0)
 safe=[list(c) for c in B.adj[h] if c is not None and c not in occ and c not in reached]
 return dict(r=d['r'],id=d['id'],L=d['L'],turn_r=t['r'],actor=a['id'],attacker_L=a['L'],dirs=a['dirs'],visible=a['id'] in vis,free_exposed=end in reached,safe=safe,local_ally=len(ally),local_enemy=len(enemy),split=t['split'],queen=d['id']==own,short_candidate=d['id']>1 and t['L']<=4 and not t['split'] and bool(t['dirs']) and len(ally)<=len(enemy) and end in reached and bool(safe))

def main():
 jobs=[];seen=set();ignored=0
 folders=[(p.name[:-4],p) for p in sorted(Path('data/online/smoke').glob('one6-*-old'))]+[('one6-live',p) for p in sorted(Path('data/online/live-one1').glob('b*'))]
 for label,folder in folders:
  for mp in sorted(folder.glob('game-*.json')):
   m=json.loads(mp.read_text());rp=mp.with_name('M%d.replay'%m['id']);own=int(m['teamAId']!=1119)
   if not rp.exists() or m['id'] in seen:continue
   if prior.replay.load(rp).root().text(1+own)!='21033':ignored+=1;continue
   seen.add(m['id']);jobs.append((label,rp,m,own))
 (OUT/'inventory.json').write_text(json.dumps(dict(time=datetime.now().astimezone().isoformat(),games=[dict(label=l,path=str(p),gid=m['id'],sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for l,p,m,o in jobs],other_submission_ignored=ignored),indent=2))
 results=[]
 for label,rp,m,own in jobs:
  fp=OUT/f"set-{m['id']}.json"
  if fp.exists():x=json.loads(fp.read_text())
  else:
   g=prior.o1_scan.scan(label,rp,m);d=prior.extra(rp,m);a=audit(rp,own);B=Board(rp)
   inds=[v for z in a['deaths'] if (v:=indicators(z,B,own))]
   for r,s in g['snaps'].items():assert [q[:4] for q in s]==d['all_snapshots'][int(r)]
   x=dict(label=label,gid=m['id'],map=m['mapName'],scan=g,detail=d,indicators=inds)
   fp.write_text(json.dumps(x,separators=(',',':')))
  results.append(x);print(label,m['id'],flush=True)
 tables={}
 for label in sorted({x['label'] for x in results}):
  xs=[x for x in results if x['label']==label];I=[i for x in xs for i in x['indicators']]
  tables[label]=dict(games=len(xs),eliminated=sum(x['scan']['how']=='elim' and x['scan']['result']=='loss' for x in xs),qdead=sum(any(z['side']==0 and z['queen'] for z in x['detail']['deaths']) for x in xs),short_rammed=sum(z[1]==0 and not z[6] and z[2]<=4 and z[4]=='rammed' for x in xs for z in x['scan']['deaths']),short_visible=sum(i['L']<=4 and not i['queen'] and i['visible'] for i in I),candidate_turns=sum(i['short_candidate'] for i in I),candidate_games=sum(any(i['short_candidate'] for i in x['indicators']) for x in xs))
 (OUT/'counts.json').write_text(json.dumps(tables,indent=2));print(json.dumps(tables,indent=2))
 print('target indicators',json.dumps(next(x['indicators'] for x in results if x['gid']==1476178),indent=2))
if __name__=='__main__':main()

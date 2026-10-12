import sys
sys.dont_write_bytecode=True
import json,gzip
from collections import Counter,defaultdict
from pathlib import Path
O=Path(__file__).resolve().parent;inv=json.loads((O/'inventory.json').read_text());by=defaultdict(Counter);moments=defaultdict(list)
for j in inv['games']:
 v=j['version'];rows=json.load(gzip.open(O/f'turns-{j["gid"]}.json.gz','rt'));c=by[v]
 for r in rows:
  q=r['q'];seen=list(r['seen'].values())
  tags=[]
  if q:
   if any(x['edge'] for x in seen):tags.append('queen_edge_contact')
   if any(x['cut'] for x in seen):tags.append('queen_true_cut_contact')
   if r.get('portal_options'):tags.append('queen_portal_choice')
   if r.get('unseen_portal_options'):tags.append('queen_direct_history_unknown_portal_choice')
   if r.get('portals'):
    tags.append('queen_portal_entry')
    if any(not p['exit_seen'] for p in r['portals']):tags.append('queen_direct_history_unknown_portal_entry')
   if r.get('open_start')==0:tags.append('queen_no_open_step')
  else:
   if r['L']<=4 and any(x['parts'] in (3,4) for x in seen):tags.append('small_sprint_visible_length_gate')
   if r['L']<=4 and r['dirs'] and not r['split'] and r['ally_heads']+1<=r['enemy_heads']:tags.append('short_evade_observable_gate_only')
  for tag in tags:
   c[tag]+=1;c[tag+'_'+r['next5']]+=1
   if len(moments[v,tag])<3:moments[v,tag].append(dict(gid=j['gid'],r=r['r'],id=r['id'],next5=r['next5'],death_r=r.get('death_r')))
result=dict(versions={str(k):dict(v) for k,v in by.items()},examples={f'{v}:{tag}':xs for (v,tag),xs in moments.items()},warning='Gate and observed-action outcomes only, NOT actual switch-caused changes. Memory, attack, leader and candidate scores not reconstructed.')
(O/'feature-observations.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
for v,c in sorted(by.items()):print(v,dict(c))

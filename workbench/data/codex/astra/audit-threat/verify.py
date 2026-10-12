import sys
sys.dont_write_bytecode=True
import json,gzip
from collections import Counter
import audit as a
O=a.OUT
inv=json.loads((O/'inventory.json').read_text());gs=[j for j in inv['games'] if (O/f'g{j["gid"]}.json').exists()]
assert len({j['gid'] for j in gs})==len(gs)
old=json.loads((O/'validation.json').read_text()) if (O/'validation.json').exists() else {}
checks=old.get('checks',[])
checked={c['gid'] for c in checks}
for j in gs:
 if j['gid'] in checked:continue
 g=json.loads((O/f'g{j["gid"]}.json').read_text())
 rows=json.load(gzip.open(O/f'turns-{j["gid"]}.json.gz','rt'))
 assert sum(r['q'] for r in rows)==g['counts']['queen_turns']
 assert sum(not r['q'] for r in rows)==g['counts']['other_turns']
 assert sum(r['ate'] for r in rows if r['q'])==g['counts'].get('queen_pearls',0)
 assert sum(r['ate'] for r in rows if not r['q'] and r['L']<=4)==g['counts'].get('short_pearls',0)
 assert sum(g['qlens'].values())==g['counts']['queen_turns']
 root=a.sb.load_replay(a.ROOT/j['path']).root();own=0 if j['meta']['teamAId']==1119 else 1
 assert root.text(1+own)==j['bot']
 rawdeath=[];actor=None;logs=Counter();births={}
 for idx,ev in enumerate(root.pointer(3)):
  k=ev.u16(0);p=ev.pointer(0)
  if k==1:actor=p.i32(0)
  elif k==6:logs[p.i32(0)]+=1
  elif k==10:births[p.i32(4)]=idx
  elif k==11:rawdeath.append((p.i32(0),p.u16(4),actor))
 victims={d['id'] for d in g['deaths']}
 ours_ram=[(i,actor) for i,reason,actor in rawdeath if i in victims and reason==3 and i!=actor and any(r['id']==i for r in g['rams'])]
 assert Counter(ours_ram)==Counter((r['id'],r['attacker']) for r in g['rams'])
 for r in g['rams']:
  r['born_after_decision']=bool(r['turn'] and births.get(r['attacker'],-1)>r['turn']['seq'])
 (O/f'g{j["gid"]}.json').write_text(json.dumps(g,ensure_ascii=False,separators=(',',':')))
 checks.append(dict(gid=j['gid'],bot=j['bot'],turns=len(rows),rams=len(g['rams']),all_dragon_log_events=sum(logs.values())))
print('checks',len(checks),'logs',sum(c['all_dragon_log_events'] for c in checks),flush=True)
# Independent full-state reader/counter checks all of one9 and one10 plus a baseline sample.
a.lr.replay.load=a.sb.load_replay
ind=old.get('independent',[])
ind_checked={c['gid'] for c in ind}
for j in gs:
 if j['gid'] in ind_checked:continue
 if j['version'] not in (9,10) and j['gid'] not in (1472003,1480434,1483011):continue
 g=json.loads((O/f'g{j["gid"]}.json').read_text());ref=a.lr.scan(a.ROOT/j['path'],j['meta'],'audit-threat',set())
 rd=[d for d in ref['deaths'] if d['side']=='us']
 assert Counter((d['id'],d['round'],d['reason']) for d in rd)==Counter((d['id'],d['r'],d['reason']) for d in g['deaths'])
 assert ref['q_eats'].get('us',0)==g['counts'].get('queen_pearls',0)
 assert ref['final']['us']['queen_length']==g['qfinal']
 qq=next((d for d in rd if d['id']==g['queen']),None)
 item=dict(gid=j['gid'],deaths=len(rd),queen_death=qq);ind.append(item)
 print('independent',j['gid'],qq['cause'] if qq else 'alive',qq.get('hit') if qq else '',flush=True)
(O/'validation.json').write_text(json.dumps(dict(checks=checks,independent=ind),ensure_ascii=False,indent=2))

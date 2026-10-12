import sys
sys.dont_write_bytecode=True
import json
from collections import Counter,deque
from pathlib import Path
sys.path.insert(0,'tools')
from ladder_replay import edge_id,canonical_edges
OUT=Path(__file__).resolve().parent
rows=[]
for gid in (1494956,1494960,1494963,1494966,1494967):
    base=json.loads((OUT/f'{gid}-base.json').read_text())
    trace=json.loads((OUT/f'{gid}-trace.json').read_text())
    w,h=map(int,base['text'].splitlines()[0].split()[1:3])
    edges=canonical_edges(w,h,[tuple(map(int,line.split()[1:4])) for line in base['text'].splitlines() if line.startswith('EDGE ')])
    def dist(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1])
        return min(dx,w-dx)+min(dy,h-dy)
    def inview(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1])
        return max(min(dx,w-dx),min(dy,h-dy))<=3
    ours=[t for t in trace['turns'] if t['s']==0]
    qs=[t for t in ours if t['queen']]
    ate=[t for t in ours if not t['queen'] and t['steps'] and list(t['steps'][0]) in t['adjpearls']
         and tuple(t['steps'][0]) in map(tuple,t['eaten']) and t['dirs']
         and edges.get(edge_id(w,h,*t['h'],t['dirs'][0]),(0,-1))[0]==0]
    straight=[t for t in ours if t['r']<12 and t['L']<=4 and not t['queen'] and t['dirs'] and t['facing']==t['dirs'][0] and len(t['exits'])>=2]
    misses=[t for t in ours if t['adjpearls'] and not t['eaten'] and not t['split'] and t['end'] is not None]
    stops=[d for d in base['deaths'] if d['side']=='us' and d['reason']==4]
    stopids={d['death'] for d in stops}
    drop=[pr for pr in base['pearls'] if pr['death'] in stopids]
    rams=[t for t in ours if any(d['i']==trace['queens'][1] and d['reason']==3 for d in t['deaths'])]
    actual_kinds=Counter(d['reason'] for d in base['deaths'] if d['side']=='us')
    def moments(ts,keys):return [{k:t[k] for k in keys} for t in ts[:3]]
    row=dict(gid=gid,cells=w*h,own_turns=len(ours),logs=len(trace['logs']),
        ordinary_adjacent_eats=len(ate),eat_moments=moments(ate,['r','i','L','h','dirs','eaten']),
        heading_continuations=len(straight),heading_moments=moments(straight,['r','i','L','h','dirs']),
        adjacent_pearl_noeat_survived=len(misses),miss_moments=moments(misses,['r','i','L','h','dirs','adjpearls']),
        stationary_alive_without_split=sum(t['h']==t['end'] and not t['split'] for t in ours),
        own_queen_rams=len(rams),ram_moments=moments(rams,['r','i','L','h','qpath','dirs','deaths']),
        stops=len(stops),stop_dropped_pearls=len(drop),stop_pearls_eaten_by_queen=sum(pr['eater_id']==trace['queens'][0] for pr in drop),
        stop_recovery=Counter(pr['eater'] for pr in drop),stop_deaths_no_us_recovery=sum(not any(pr['eater']=='us' and pr['death']==d['death'] for pr in drop) for d in stops),
        high_portal_ids=len({pid for kind,pid in edges.values() if kind==2 and pid>=2*w*h}),
        qL4_unsplit=sum(t['L']==4 and t['n']>=2 and not t['split'] for t in qs),
        qlength_preserve_moments=moments([t for t in qs if t['L']==4 and t['n']>=2 and not t['split']],['r','i','L','n','h','dirs']),
        death_reasons=actual_kinds)
    for s in ('us','them'):
        assert base['final'][s]['pearls']==sum(base['eats'][s].values())
    rows.append(row)
total={k:sum(r[k] for r in rows) for k in ['own_turns','logs','ordinary_adjacent_eats','heading_continuations',
    'adjacent_pearl_noeat_survived','stationary_alive_without_split','own_queen_rams','stops','stop_dropped_pearls',
    'stop_pearls_eaten_by_queen','stop_deaths_no_us_recovery','high_portal_ids','qL4_unsplit']}
total['stop_recovery']=dict(sum((Counter(r['stop_recovery']) for r in rows),Counter()))
movement=json.loads((OUT/'movement.json').read_text())
for k in ['mate_risk_choice','pocket_choice','target_geometry']:
    total[k]=sum(r['counts'].get(k,0) for r in movement)
(OUT/'evidence.json').write_text(json.dumps(dict(totals=total,games=rows),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(total,ensure_ascii=False))

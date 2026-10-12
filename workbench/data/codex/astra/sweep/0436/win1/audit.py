import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import Counter, deque
sys.path.insert(0,'tools')
sys.path.insert(0,'data/analysis/ladder/dossier/work')
from ladder_replay import replay,edge_id,canonical_edges
from o1_qdef import scan as guard_scan
OUT=Path(__file__).resolve().parent
counts,games=Counter(),Counter();details=[]
for f in sorted(OUT.glob('1*.json')):
    d=json.loads(f.read_text()); ts=[json.loads(x) for x in (OUT/f'{d["gid"]}-turns.jsonl').read_text().splitlines()]
    own=[t for t in ts if t['s']==0]; one9=int(d['bot'])==21165
    groups={
      'eat_adj':[t for t in own if t['adjp'] and any(c in t['adjp'] for c in t['eaten'])],
      'heading':[t for t in own if t['r']<12 and t['id']>1 and t['directions'] and t['directions'][0]==t['prior_dir']],
      'herd_nearer':d['signatureExamples']['herd_nearer'],
      'queen_exit_kept':[t for t in own if t['steps'] and any(z['queen'] and z['cell'] not in t['steps'] for z in t['last_exit_choices'])],
      'mate_exit_kept':[t for t in own if t['steps'] and any(not z['queen'] and z['cell'] not in t['steps'] for z in t['last_exit_choices'])],
      'pocket_short':[t for t in own if t['L']<4 and t['pocket_pearl_choices'] and t['steps'] and not t['split'] and not any(c in t['steps'] for c in t['pocket_pearl_choices'])],
      'qs_relax':[t for t in own if t['id']==d['queenIds'][0] and t['split'] and t['L']==4 and t['ownN']<(6 if one9 else 2)],
      'missed_survived':[t for t in own if t['adjp'] and t['alive'] and not t['split'] and not any(c in t['adjp'] for c in t['eaten'])],
      'idle_survived':[t for t in own if not t['split'] and not t['steps'] and t['alive'] and t.get('actionKind')==0],
      'cap_stops':[t for t in own if 350<t['r']<400 and t['ownN']>=56 and t['death']==4 and t['free']>0],
      'sure_queen':[q for q in d['queenDeaths'] if q['side']==1 and q['reason']==3 and q['actorSide']==0 and q['actorL0']<=4 and q['stepsTaken']+1<=3],
    }
    guard=guard_scan('0436',Path(d['path']),d['meta'])
    groups['guard_candidate']=[g for g in guard['guard'] if g[1]<=4 and g[5]<=3 and g[7]<=g[6]]
    groups['guard_ram']=[g for g in groups['guard_candidate'] if g[8]]
    root=replay.load(d['path']).root(); bodies={};teams={};raw=[]
    for line in root.text(0).splitlines():
      q=line.split()
      if q and q[0]=='DRAGON':
        i=len(bodies);teams[i]=int(q[1]);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])))
      elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
    edges=canonical_edges(d['W'],d['H'],raw);rnd=-1;portal=[]
    for ev in root.pointer(3):
      k=ev.u16(0);p=ev.pointer(0)
      if k==0:rnd=p.i32(0)
      elif k==9:
        i=p.i32(0);head,tail=replay.point(p.pointer(0)),replay.point(p.pointer(1));b=bodies[i]
        if b[0]!=head:b.appendleft(head)
        while len(b)>1 and b[-1]!=tail:b.pop()
        assert b[-1]==tail
      elif k==10:
        i,ch=p.i32(0),p.i32(4);L=len(bodies[i]);tail=bodies[i][-1]
        if one9 and teams[i]==0 and i!=d['queenIds'][0] and L==4 and rnd<=100 and any(edges.get(edge_id(d['W'],d['H'],*tail,di),(0,-1))[0]==2 for di in range(4)):
          portal.append(dict(r=rnd,id=i,L=L,tail=tail))
        for z,n in enumerate((i,ch)):
          bodies[n]=deque(replay.point(c) for c in p.pointer(z));teams[n]=p.u16(8)
      elif k==11:del bodies[p.i32(0)]
    groups['portal_split']=portal
    local={key:len(value) for key,value in groups.items()};local['herd_nearer']=d['signatureCounts']['herd_nearer']
    counts.update(local);games.update(key for key,n in local.items() if n)
    detail=dict(gid=d['gid'],counts=local,examples={k:v[:3] for k,v in groups.items()},queen_risk=guard['death'])
    details.append(detail);print(d['gid'],local,flush=True)
(OUT/'audit.json').write_text(json.dumps(dict(counts=dict(counts),games=dict(games),details=details),ensure_ascii=False,indent=2)+'\n')

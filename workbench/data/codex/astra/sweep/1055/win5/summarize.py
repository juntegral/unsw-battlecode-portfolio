import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
from collections import Counter
from analyze import OUT, JOBS

rows=[]; aggregate=Counter(); examples={}
for gid,folder in JOBS:
    p=OUT/f'{gid}.json'
    if not p.exists(): continue
    r=json.loads(p.read_text()); q=r['queens'][0]
    ts=[json.loads(line) for line in (OUT/f'{gid}-turns.jsonl').open()]
    own=[t for t in ts if t['s']==0]
    qts=[t for t in own if t['id']==q]
    qd=[d for d in r['deaths'] if d['queen']]
    last=r['states'].get(str(r['ahead']-1))
    print('\nGAME',gid,r['meta']['mapName'],'ahead prior',last,'final',r['ledger']['ends'],flush=True)
    print('queen deaths',qd,flush=True)
    print('one-step risk',r['risks'][:3],flush=True)
    if qd and any(d['s']==0 for d in qd):
        d=next(d for d in qd if d['s']==0)
        print('last queen turns',qts[-2:],flush=True)
        print('death actor turns',[t for t in ts if t['r']==d['r'] and t['id']==d['actor']],flush=True)
    for k,v in r['signatures'].items():
        aggregate[k]+=v['n']; aggregate[k+'_games']+=v['n']>0
        if v['n']:examples.setdefault(k,[]).extend([dict(gid=gid,r=t['r'],id=t['id']) for t in v['examples'][:1]])
    modes={
        'small_sprint_threat_condition':[t for t in own if t['L']<=4 and t['visible_enemies']],
        'late_stops':[t for t in own if t['r']>350 and t['death']==4 and t['free']],
        'queen_low_keep':[t for t in qts if t['L']>=4 and t['N']>=2 and not t['split']],
        'sure_queen_rams':[d for d in r['deaths'] if d['queen'] and d['s']==1 and d['reason']==3 and d['actorSide']==0 and d['actorL']<=64],
        'long_rammed':[d for d in r['deaths'] if d['s']==0 and d['L']>=8 and d['reason']==3 and d['actorSide']==1],
    }
    # Heading uses each dragon's last actual movement, without an arbitrary lookback.
    modes['heading_continue']=[]; facing={}
    for t in ts:
        if t['s']==0 and t['r']<12 and t['id']!=q and t['dirs'] and t['dirs'][0]==facing.get(t['id']):
            modes['heading_continue'].append(t)
        if t['dirs'] and t['steps']: facing[t['id']]=t['dirs'][min(len(t['steps']),len(t['dirs']))-1]
    for k,v in modes.items():
        aggregate[k]+=len(v);aggregate[k+'_games']+=bool(v)
        if v:examples.setdefault(k,[]).append(dict(gid=gid,r=v[0].get('r'),id=v[0].get('id')))
    counts={k:v['n'] for k,v in r['signatures'].items()}
    print('signatures',counts,'modes',{k:len(v) for k,v in modes.items()},flush=True)
    for k in ('blind_portal_declined','long_sprint','pass_adj'):
        print(k,r['signatures'][k]['examples'][:1],flush=True)
    rows.append(dict(gid=gid,counts=counts,prior=last,queenDeaths=qd,risks=r['risks']))
(OUT/'counts.json').write_text(json.dumps(dict(counts=dict(aggregate),examples=examples,rows=rows),ensure_ascii=False,indent=2)+'\n')
print('\nTOTAL',dict(aggregate),flush=True)

import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
sys.path.insert(0,'tools')
import ladder_replay as lr

D=Path(__file__).resolve().parent
jobs=[(1490641,1490641),(1490642,1490641),(1490645,1490641),(1490797,1490796)]
summary=[]
for gid,folder in jobs:
    raw=json.loads((D/f'raw-{gid}.json').read_text())
    ledger=json.loads((D/f'ledger-{gid}.json').read_text())
    turns=[json.loads(x) for x in (D/f'turns-{gid}.jsonl').read_text().splitlines()]
    root=lr.replay.load(f'data/online/live-one1/b{folder}/M{gid}.replay').root()
    starters=[l.split() for l in root.text(0).splitlines() if l.startswith('DRAGON ')]
    ours='AB'.index(raw['ours'])
    residuals=[]
    for s in (0,1):
        initial=sum(int(l[2]) for l in starters if int(l[1])==(ours if s==0 else 1-ours))
        eaten=sum(e[1]==s for e in ledger['eats'])
        lost=sum(e[2] for e in ledger['deaths'] if e[1]==s)
        paid=sum(e[3] for e in ledger['paids'] if e[1]==s)
        final=raw['final']['us' if s==0 else 'them']
        assert (final['alive'],final['total'],final['longest'],final['queen_length'])==tuple(ledger['ends'][s][:4])
        residual=initial+eaten-lost-paid-final['total']
        assert residual==0,(gid,s,residual)
        residuals.append(residual)
    key=lambda v:(int(v['alive']>0),v['queen_length'],v['longest'],v['total'])
    last_bad=max((int(r) for r,v in raw['snapshots'].items() if key(v['us'])<=key(v['them'])),default=-1)
    queen=raw['queens']['us']; enemy_queen=raw['queens']['them']
    attacks=[{k:t[k] for k in ('r','id','L','dirs','queen_alive')} for t in turns if any(d[0]==enemy_queen and d[1]==3 for d in t['deaths'])]
    cuts=[t for t in turns if t['id']==queen and any(f[0]!=enemy_queen and f[2]<4 for f in t['cut'])]
    pearl_opps=[t for t in turns if t['adjacent']]
    took=sum(bool(t['steps']) and t['steps'][0][1] in [p[1] for p in t['adjacent']] for t in pearl_opps)
    stops=[t for t in turns if t['action']==2]
    donors=[]
    for t in stops:
        death=next(d for d in raw['deaths'] if d['id']==t['id'] and d['round']==t['r'])
        pearls=[p for p in raw['pearls'] if p['death']==death['death']]
        donors.append(dict(round=t['r'],id=t['id'],length=t['L'],queen_length=len(t['queen']),
                           queen_eaten=sum(p['eater_id']==queen for p in pearls),
                           own_eaten=sum(p['eater']=='us' for p in pearls),
                           enemy_eaten=sum(p['eater']=='them' for p in pearls),
                           uneaten=sum(p['eater']=='nobody' for p in pearls)))
    summary.append(dict(gid=gid,bot=raw['bots'][raw['ours']],ours=raw['ours'],final=raw['final'],
                        last_round=raw['last_round'],permanent_round_end_lead=last_bad+1,
                        ledger_residuals=residuals,queen_attacks=attacks,
                        cut_nonqueen_visible_under4_turns=len(cuts),
                        cut_examples=[dict(round=t['r'],enemies=t['cut'],action=t['dirs']) for t in cuts[:3]],
                        adjacent_pearl_turns=len(pearl_opps),first_step_takes_adjacent_pearl=took,
                        no_action_donors=donors,
                        queen_splits=[dict(round=t['r'],length=t['L'],units=t['unit_count']) for t in turns if t['id']==queen and t['split']],
                        max_own_turn_start_units=max(t['unit_count'] for t in turns),
                        queen_adjacent_pearl_misses=[t['r'] for t in pearl_opps if t['id']==queen and not(t['steps'] and t['steps'][0][1] in [p[1] for p in t['adjacent']])]))
(D/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps([{k:v for k,v in r.items() if k not in ('no_action_donors','cut_examples','queen_adjacent_pearl_misses')} for r in summary],ensure_ascii=False,indent=2))

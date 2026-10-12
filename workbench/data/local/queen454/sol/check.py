#!/usr/bin/env python3
"""Cross-check official ladder fields and direct replay events; writes only to sol/."""
import sys
sys.dont_write_bytecode=True
import json,random,concurrent.futures
from pathlib import Path
from collections import Counter
sys.path.insert(0,'~/01. Project/개인 프로젝트/battlecode')
import replay as R
OUT=Path(__file__).resolve().parent

def direct(row):
    root=R.load(row['replay']).root();qt=row['queen_id'];actor=None;roundno=0;ph=Counter();deaths=[];splits=[];eats=0;actions=0;kind=None
    for ev in root.pointer(3):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:roundno=p.i32(0)+1;actor=None;kind=None
        elif k==1:actor=p.i32(0);kind=None
        elif k==4:
            actor=p.i32(0);a=p.pointer(0);kind=a.u16(0) if a else None
            if actor==qt:actions+=1
        elif k==3 and not p.bit(0) and actor==qt and kind==0:eats+=1
        elif k==10 and p.i32(0)==qt:splits.append(roundno)
        elif k==11 and p.i32(0)==qt:deaths.append((roundno,p.u16(4)))
    counted=sum(p['pearls'] for p in row['phases'].values())
    assert eats==counted,(row['game'],'pearls')
    assert actions==sum(p['actions'] for p in row['phases'].values()),(row['game'],'actions')
    assert splits==row['split_rounds'],(row['game'],'splits')
    assert sum(r>200 for r in splits)==row['splits_after_200']
    expected=[(row['death']['round'],row['death']['raw_reason'])] if row['death'] else []
    assert deaths==expected,(row['game'],'death')
    return row['game']

def main():
    rows=json.loads((OUT/'rows.json').read_text());keys=[(r['group'],r['game']) for r in rows];assert len(set(keys))==len(keys)==503
    assert Counter(r['group'] for r in rows)=={'aAah':101,'ours':370,'38 off':16,'38 on':16}
    ladder={x['game']:x for l in Path('data/analysis/ladder/rows.jsonl').read_text().splitlines() if l and (x:=json.loads(l)).get('our_bot',{}).get('version') in (44,47)}
    warnings=[];same=0;exposure_checks=0;closure_checks=0
    for row in rows:
        assert row['verified_final_state']
        assert row['alive_end']==(row['death'] is None)
        assert sum(x['splits'] for x in row['phases'].values())==len(row['split_rounds'])
        for p,x in row['phases'].items():
            assert x['closer']+x['farther']+x['same']==x['visible_steps']
            assert x['loop_rounds']<=x['actions']
            assert x['lap_2x2']<=x['loop_rounds']
            exposure_checks+=1
        for col in row['collisions']:
            a=col['previous_5_rounds']
            if a['complete_history'] and a['distance_at_contact_round_start'] is not None:
                delta=a['distance_before']-a['distance_at_contact_round_start']
                assert delta==a['queen_closing_steps']+a['enemy_closing_steps'],(row['game'],col['round'],'closing decomposition',delta,a)
                closure_checks+=1
        if row['group']=='ours':
            src=ladder[row['game']];q=src['queen']['us'];final=src['final']
            assert q['id']==row['queen_id']
            assert q['alive_end']==row['alive_end']
            assert final['us']['queen_length']==row['final_queen_lengths'][0]
            assert final['them']['queen_length']==row['final_queen_lengths'][1]
            assert q['death_round'] is None if row['death'] is None else q['death_round']+1==row['death']['round']
            same+=1
            if q.get('pearls_eaten')!=sum(p['pearls'] for p in row['phases'].values()):
                warnings.append(dict(game=row['game'],field='ladder pearls',ladder=q.get('pearls_eaten'),ours=sum(p['pearls'] for p in row['phases'].values()),note='Ladder field was not used; direct removal-event count is authoritative.'))
    random.seed(454)
    selected=[]
    for group in ('aAah','ours','38 off','38 on'):
        sub=[r for r in rows if r['group']==group]
        selected+=random.sample(sub,min(5,len(sub)))
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:direct_games=list(pool.map(direct,selected))
    result=dict(games=503,official_final_standing_checks=503,ladder_cross_checks=same,phase_exposure_checks=exposure_checks,
        exact_five_round_closing_checks=closure_checks,direct_event_audit_games=direct_games,warnings=warnings)
    (OUT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    assert len((OUT/'summary.md').read_text().splitlines())<=80
    assert len((OUT/'last.txt').read_text().splitlines())<=5
    print(json.dumps({k:v for k,v in result.items() if k!='warnings'}));print('ladder pearl differences',len(warnings))
if __name__=='__main__':main()

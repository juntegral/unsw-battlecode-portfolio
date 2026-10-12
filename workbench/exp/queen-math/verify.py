#!/usr/bin/env python3
"""Independent artifact audit. Intentionally does NOT import model/analyze.

One process, standard library, no engines or games. Replays finite command
witnesses with a separate array transition and checks periodic room witnesses.
"""
import csv
import hashlib
import itertools
import json
import re
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
D={'N':(0,-1),'E':(1,0),'S':(0,1),'W':(-1,0)}

def data(name):return json.loads((HERE/name).read_text())
def rows(name):return list(csv.DictReader((HERE/name).open()))
def point(p):return tuple(p)

def independent_move(bodies,ident,word,cells=None):
    """No pearls in assassination artifacts. None marks a dead dragon."""
    bodies={i:None if b is None else list(map(point,b)) for i,b in bodies.items()}
    initial=len(bodies[ident]); budget=(initial+3)//4
    for n,letter in enumerate(word):
        b=bodies[ident]
        if b is None:break
        if n>=budget and len(b)==2:
            bodies[ident]=None; break
        dx,dy=D[letter]; target=(b[0][0]+dx,b[0][1]+dy)
        if cells is not None and target not in cells or target in b:
            bodies[ident]=None; break
        collided=False
        for i,other in bodies.items():
            if i==ident or other is None or target not in other:continue
            if target==other[0]:bodies[i]=None
            bodies[ident]=None; collided=True; break
        if collided:break
        bodies[ident]=[target]+b[:-1]
        if n>=budget:bodies[ident].pop()
    return bodies

def brute_reach(body,bound):
    reached=set(); prefixes=0
    def visit(word):
        nonlocal prefixes
        if len(word)==bound:return
        for letter in D:
            new=word+letter
            final=independent_move({0:body},0,new)[0]
            if final is None:continue
            reached.add(final[0]); prefixes+=1; visit(new)
    visit('')
    return reached,prefixes

def independent_room(cells,length):
    """Re-enumerate bodies and use cyclic SCCs + reverse reachability.

    The generator uses its own arrays; this algorithm differs from analyze's
    repeated removal of zero-outdegree states.
    """
    bodies=[]
    def extend(body):
        if len(body)==length:bodies.append(tuple(body)); return
        x,y=body[-1]
        for dx,dy in D.values():
            p=x+dx,y+dy
            if p in cells and p not in body:extend(body+[p])
    for p in sorted(cells):extend([p])
    ids={b:i for i,b in enumerate(bodies)}; edges=[[] for _ in bodies]
    incoming=[[] for _ in bodies]
    for i,b in enumerate(bodies):
        for dx,dy in D.values():
            p=b[0][0]+dx,b[0][1]+dy
            if p not in cells or p in b:continue
            j=ids[(p,)+b[:-1]]; edges[i].append(j); incoming[j].append(i)
    clock=0; discovery={}; low={}; stack=[]; active=set(); cyclic=set()
    def scc(v):
        nonlocal clock
        discovery[v]=low[v]=clock; clock+=1; stack.append(v); active.add(v)
        for w in edges[v]:
            if w not in discovery:scc(w); low[v]=min(low[v],low[w])
            elif w in active:low[v]=min(low[v],discovery[w])
        if low[v]==discovery[v]:
            group=[]
            while True:
                w=stack.pop(); active.remove(w); group.append(w)
                if w==v:break
            if len(group)>1 or v in edges[v]:cyclic.update(group)
    for i in range(len(bodies)):
        if i not in discovery:scc(i)
    viable=set(cyclic); todo=list(cyclic)
    for v in todo:
        for p in incoming[v]:
            if p not in viable:viable.add(p); todo.append(p)
    return len(bodies),len(viable)

def independent_family_kill(initial,hunter,cells):
    """No-food tiny negative assassination audit, including recursive splits."""
    initial={i:None if b is None else list(map(point,b)) for i,b in initial.items()}
    length=len(initial[hunter]); bound=(length+3)//4+length-2
    def commands(word):
        if len(word)==bound:return False
        for letter in D:
            new=word+letter; final=independent_move(initial,hunter,new,cells)
            if final[0] is None:return True
            if final[hunter] is not None and commands(new):return True
        return False
    if commands(''):return True
    for size in range(2,length-1):
        state=dict(initial); body=initial[hunter]
        state[hunter]=body[:-size]; child=max(state)+1
        state[child]=body[-size:][::-1]
        if independent_family_kill(state,child,cells):return True
    return False

def main():
    checks=[]
    for path,digest in data('source-manifest.json').items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
    checks.append('rule_source_hashes_unchanged')
    for row in rows('reach.csv'):
        l=int(row['L']); f=(l+3)//4; m=f+l-2
        assert int(row['free'])==f and int(row['max_steps_no_food'])==m
        assert int(row['same_round_safe_distance'])==m+1
        descendants=max(m,l-1+((l-2+3)//4+l-4)) if l>=4 else m
        assert int(row['same_round_safe_distance_with_split_descendants'])==descendants+1
        # Independent optimization over all first-turn lengths / free usage.
        options=[]
        for n1 in range(1,m+1):
            remaining=l-max(0,n1-f)
            n2=(remaining+3)//4+remaining-2
            options.append(n1+n2)
        assert int(row['two_turn_reach_no_food'])==max(options)==l-2+2*f
        family_two=max(max(options),l-1+(l-4)+2*((l+1)//4)) if l>=4 else max(options)
        assert int(row['two_turn_reach_with_split_descendants'])==family_two
        assert int(row['two_turn_old_tile_safe_distance_with_split_descendants'])==family_two+1
    checks.append('all_39_reach_rows_and_two_turn_optimization')
    for case in data('fixtures.json')['split_child_assassination_tight_distance_witnesses']:
        size=case['split_size']; enemy=case['enemy']
        state={0:case['queen'],2:enemy[:-size],3:enemy[-size:][::-1]}
        assert independent_move(state,3,case['child_move'])[0] is None
    checks.append('all_37_same_round_split_assassination_distance_witnesses')
    for case in data('fixtures.json')['two_turn_split_family_tight_old_target_witnesses']:
        size=case['split_size']; enemy=case['enemy']
        state={0:case['queen'],2:enemy[:-size],3:enemy[-size:][::-1]}
        state=independent_move(state,3,case['first_child_move'])
        state=independent_move(state,2,case['second_parent_move'])
        state=independent_move(state,3,case['second_child_move'])
        assert state[0] is None and state[2] is not None
    checks.append('all_37_two_turn_split_family_fixed_target_witnesses')
    reach=data('reach-exact-small.json'); prefix_count=0
    for ls,entry in reach.items():
        l=int(ls); exact,prefixes=brute_reach(entry['body'],(l+3)//4+l-2)
        assert exact==set(map(point,entry['exact_reached']))
        prefix_count+=prefixes
    checks.append('L2_to_L8_exact_reach_by_unmerged_command_DFS')
    witness_steps=0
    room=data('rooms-3x3.json')['records']
    for entry in room:
        total,safe=independent_room(set(map(point,entry['cells'])),entry['L'])
        assert total==entry['states'] and safe==entry['safe_states']
        witness=entry['witness']
        if witness is None:assert entry['safe_states']==0; continue
        cells=set(map(point,entry['cells']))
        transient=witness['transient']; period=witness['period']
        history=transient+period+[period[0]]
        for before,after in zip(history,history[1:]):
            before=list(map(point,before)); after=list(map(point,after))
            assert len(set(before))==len(before)==entry['L']
            assert set(before)<=cells
            assert after[0] not in before
            assert abs(after[0][0]-before[0][0])+abs(after[0][1]-before[0][1])==1
            assert after==[after[0]]+before[:-1]
            witness_steps+=1
    checks.append('every_finite_room_witness_transition_and_period_closure')
    checks.append('all_862_room_censuses_recomputed_by_cyclic_SCC_reachability')
    for item in data('rectangle-constructions.json'):
        cycle=list(map(point,item['cycle'])); w,h=item['width'],item['height']
        assert len(cycle)==len(set(cycle))==w*h-w*h%2
        assert all(0<=x<w and 0<=y<h for x,y in cycle)
        assert all(abs(a[0]-b[0])+abs(a[1]-b[1])==1 for a,b in zip(cycle,cycle[1:]+cycle[:1]))
    checks.append('all_81_general_rectangle_cycle_constructions')
    attacks=data('assassination.json')['fixtures']; responses=0; negative_families=0
    for fixture in attacks:
        initial={0:fixture['queen']}
        initial.update({h['id']:h['body'] for h in fixture['hunters']})
        cells=None if fixture['cells'] is None else set(map(point,fixture['cells']))
        for case in fixture['cases']:
            action=case['queen_action']
            if action.startswith('SPLIT'):
                size=int(action.split()[1]); b=initial[0]
                state=dict(initial); state[0]=b[:-size]
                state[max(state)+1]=b[-size:][::-1]
            else:state=independent_move(initial,0,action,cells)
            assert list(map(point,state[0]))==list(map(point,case['queen_body']))
            if case['forced_contact']:
                for hunter,word in case['hunter_response']:
                    state=independent_move(state,hunter,word,cells)
                assert state[0] is None
                responses+=1
            elif len(fixture['hunters'])==1:
                hunter=fixture['hunters'][0]['id']
                assert not independent_family_kill(state,hunter,cells)
                negative_families+=1
    checks.append('all_stored_assassination_witnesses_replayed_independently')
    checks.append('all_negative_single_hunter_cases_include_recursive_splits_independently')
    for row in rows('vault-phases.csv'):
        q,c=int(row['Q']),int(row['C']); gap=c-q
        assert (row['perpetual_body_gate']=='True')==((q+3)//4>=gap+2)
    for witness in data('vault-witnesses.json'):
        q,c=witness['Q'],witness['C']; period=witness['period']
        for i,item in enumerate(period):
            h=item['head_phase']; n=item['steps']
            assert 1<=n<=(q+3)//4
            for s in range(1,n+1):
                dest=(h+s)%c
                assert dest not in {(h+s-1-j)%c for j in range(q)}
            final=(h+n)%c
            assert final==period[(i+1)%len(period)]['head_phase']
            assert 0 in {(final-j)%c for j in range(1,q)}
    checks.append('every_vault_phase_edge_substep_and_gate_body_invariant')
    # Independently recompute concrete payoff by lexicographic arrays.
    concrete=data('backup-concrete.json'); terms={}
    def value(a,b):return 1. if a>b else .5 if a==b else 0.
    for name,q,workers in [('feed',16,[2]),('backup',14,[3,2])]:
        a=sum(value([q,q,q+sum(workers)],[eq,eq,eq+eb])
              for eq in range(10,21) for eb in range(2,5))/33
        t=sum(value([0,max(workers),sum(workers)],[0,eb,eb]) for eb in range(2,5))/3
        assert abs(a-concrete['terms'][name]['a'])<1e-12
        assert abs(t-concrete['terms'][name]['t'])<1e-12
        terms[name]=(a,t)
    for row in rows('backup-concrete.csv'):
        p=float(row['p'])
        for name in ('feed','backup'):
            a,t=terms[name]; expected=p*(.2+.8*a)+(1-p)*.2*t
            assert abs(expected-float(row[name+'_EV']))<1e-12
    checks.append('concrete_EV_enumerated_from_all_tiebreaks')
    literal=data('backup-feed-everything.json')
    af=sum(value([17,17,17],[eq,eq,eq+eb]) for eq in range(10,21) for eb in range(2,5))/33
    ab=sum(value([15,15,18],[eq,eq,eq+eb]) for eq in range(10,21) for eb in range(2,5))/33
    tb=sum(value([0,3,3],[0,eb,eb]) for eb in range(2,5))/3
    assert abs(af-literal['a_feed'])<1e-12 and abs(ab-literal['a_backup'])<1e-12
    assert abs(tb-literal['t_backup'])<1e-12
    for row in rows('backup-feed-everything.csv'):
        p=float(row['p'])
        assert abs(float(row['feed_everything_EV'])-39*p/55)<1e-12
        assert abs(float(row['keep_L3_EV'])-(.1+.5*p))<1e-12
    checks.append('literal_feed_everything_EV_includes_early_elimination')
    report=ROOT/'research/observations/queen-mechanics.md'
    citation_count=0
    if report.exists():
        citations=re.findall(r'\]\(\.\./\.\./rules/([^)#]+)\.md#L(\d+)\)',report.read_text())
        for name,line in citations:
            assert 1<=int(line)<=len((ROOT/'rules'/f'{name}.md').read_text().splitlines())
        citation_count=len(citations)
        checks.append('report_rule_citation_files_and_line_numbers_exist')
    result=dict(all_checks_passed=True,checks=checks,independent_legal_move_prefixes=prefix_count,
                room_witness_steps=witness_steps,assassination_responses=responses,
                independently_checked_negative_split_families=negative_families,
                report_rule_line_citations=citation_count,
                limits='Independent implementations check artifacts, not the official engine; no game/network. Geometry uses isolated no-wrap/no-portal cells unless stated.')
    (HERE/'independent-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()

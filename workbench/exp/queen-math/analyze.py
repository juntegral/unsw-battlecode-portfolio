#!/usr/bin/env python3
"""Run with: nice -n 10 python3 exp/queen-math/analyze.py

One process, standard library only. Rebuilds generated artifacts, never SUMMARY.
Small boards are isolated subgraphs embedded in a legal >=10x10 map, not matches.
"""
import csv
import hashlib
import json
from collections import deque
from pathlib import Path
from itertools import combinations
from model import Dragon, World, DIRS, LETTERS, add, free, maximum, diamond
from model import move_states, attack_path, family_attack_actions, score

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent

def dump(name, obj):
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")

def table(name, rows):
    with (OUT / name).open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def straight(ident, length, head=(0, 0), team=0):
    return Dragon(ident, team, tuple((head[0] - i, head[1]) for i in range(length)))

def reach_tables():
    rows, tiles, small, unions = [], {}, {}, {}
    for length in range(2, 41):
        f, m = free(length), maximum(length)
        two = max(f + k + maximum(length - k) for k in range(length - 1))
        assert two == 2 * f + length - 2
        w = World([straight(0, length)])
        assert w.move(0, [DIRS[1]] * m)
        assert len(w.dragons[0].body) == 2
        assert not w.move(0, [DIRS[1]] * 2)
        rows.append(dict(L=length, free=f, paid_cost=1, min_length=2,
                         max_steps_no_food=m, same_round_safe_distance=m+1,
                         same_round_safe_distance_with_split_descendants=(max(m,length-1+maximum(length-2)) if length>=4 else m)+1,
                         two_turn_reach_no_food=two,
                         two_turn_old_tile_safe_distance=two+1,
                         two_turn_reach_with_split_descendants=max(two,length-1+2*free(length-2)+length-4) if length>=4 else two,
                         two_turn_old_tile_safe_distance_with_split_descendants=(max(two,length-1+2*free(length-2)+length-4) if length>=4 else two)+1,
                         envelope_tiles=1+2*m*(m+1),
                         possible_some_body_tiles=2*m*(m+1)+(length>=6)))
        tiles[str(length)] = sorted(diamond(m))
        possible=diamond(m)-{(0,0)}
        origin_min=next(t for t in range(4,2*m+5,2)
                        if t-1+max(0,t-1-f)>=length)
        if origin_min<=m:possible.add((0,0))
        assert ((0,0) in possible)==(length>=6)
        # Construct and simulate a witness for EVERY member of the union over
        # arbitrary initial bodies. Use a straight neck opposite the first step.
        for x,y in sorted(possible):
            if (x,y)==(0,0):
                h=origin_min//2-1
                dirs=[DIRS[1]]+[DIRS[0]]*h+[DIRS[3]]+[DIRS[2]]*h
            else:
                dirs=([DIRS[1] if x>0 else DIRS[3]]*abs(x)+
                      [DIRS[2] if y>0 else DIRS[0]]*abs(y))
            dx,dy=dirs[0]
            body=tuple((-i*dx,-i*dy) for i in range(length))
            witness=World([Dragon(0,0,body)])
            assert witness.move(0,dirs) and witness.dragons[0].body[0]==(x,y)
        unions[str(length)]=dict(tiles=sorted(possible),
                                 move_or_legal_split_tiles=sorted(possible|({(0,0)} if length>=4 else set())),
                                 free_tiles=sorted(diamond(f)-{(0,0)}),origin_shortest_possible_steps=origin_min,
                                 all_tiles_have_simulated_constructive_witness=True)
        if length <= 8:
            states = move_states(World([straight(0, length)]), 0)
            reached = {x.dragons[0].body[0] for x, _ in states}
            assert reached <= diamond(m)
            small[str(length)] = dict(body=straight(0, length).body,
                                     exact_reached=sorted(reached),
                                     missing_from_envelope=sorted(diamond(m)-reached),
                                     move_prefix_states=len(states))
    table("reach.csv", rows)
    dump("reach-envelopes.json", dict(assumptions="no pearls, no portals, unwrapped; conservative head-only envelopes, NOT exact body-conditioned reach", lengths=tiles))
    dump("reach-exact-small.json", small)
    dump("reach-union-over-bodies.json",dict(scope="Exact union over ALL possible initial body placements/facings, no pearls/portals/wrap, nonempty MOVE only; NOT the reach set of a particular dragon",lengths=unions))
    text = []
    for l, data in small.items():
        m = maximum(int(l))
        reached = {tuple(p) for p in data["exact_reached"]}
        body = {tuple(p) for p in data["body"]}
        text.append(f"L={l}, east-facing straight body; o=reachable, x=envelope but unreachable, H=start\n")
        for y in range(-m, m+1):
            text.append("".join("H" if (x,y)==(0,0) else "o" if (x,y) in reached else "x" if abs(x)+abs(y)<=m else " " for x in range(-m,m+1)))
        text.append("")
    (OUT / "reach-pictures.txt").write_text("\n".join(text)+"\n")
    return rows

def checks_and_feeding():
    checks, traces = [], {}
    def check(name, result):
        assert result, name
        checks.append(name)
    # Tail checked before either normal or paid tail advances.
    w = World([Dragon(0, 0, ((0,0),(1,0),(1,1),(0,1)))])
    check("own_tail_is_fatal", not w.move(0, [DIRS[2]]))
    check("fatal_step_does_not_move_head", w.events[-1]["body"][0] == (0,0))
    # Free budget remains f(4)=1 even after the first pearl grows length to five.
    w = World([straight(0,4)], pearls=[(1,0)])
    w.move(0,[DIRS[1]]*2)
    check("free_budget_fixed_at_start", len(w.dragons[0].body)==4)
    # The pearl at a paid destination cannot rescue a length-2 pre-step check.
    w = World([straight(0,2)], pearls=[(2,0)])
    w.move(0,[DIRS[1]]*2)
    check("pay_check_precedes_eating", not w.dragons[0].alive and (2,0) in w.pearls)
    # Length-2 can keep moving paid if an earlier pearl made it length three.
    w = World([straight(0,2)], pearls=[(1,0),(2,0),(3,0),(4,0)])
    check("food_extends_length_only_reach", w.move(0,[DIRS[1]]*4))
    traces["food_extension"] = w.events
    # Split keeps front/id, reverses rear, child acts in this round.
    w = World([straight(0,6), straight(1,2,(20,0),1)])
    w.round({0:("split",3),1:("move",[DIRS[1]]),2:("move",[DIRS[3]])})
    check("split_front_keeps_queen_id", w.dragons[0].body==((0,0),(-1,0),(-2,0)))
    check("child_reverse_and_same_round_turn", w.dragons[2].body==((-6,0),(-5,0),(-4,0)))
    traces["split"] = w.events
    w = World([straight(0,3)])
    check("illegal_split_kills_parent", w.split(0,2) is None and not w.dragons[0].alive)
    # Donor self-collision leaves both pearls in place ahead of the queen.
    w = World([straight(0,9), Dragon(2,0,((1,0),(2,0),(3,0)))])
    w.move(2,[DIRS[1]])
    check("L3_drops_head_and_tail", w.pearls=={(1,0),(3,0)})
    w.move(0,[DIRS[1]]*3)
    check("L3_feeder_full_collection_free", len(w.dragons[0].body)==11 and not w.pearls)
    traces["L3_feed"] = w.events
    # A donor trying to collide with a queen's head kills both BEFORE moving.
    w = World([straight(0,3), Dragon(2,0,((1,0),(2,0),(3,0)))])
    w.move(2,[DIRS[3]])
    check("friendly_head_to_head_kills_queen", not w.dragons[0].alive and not w.dragons[2].alive)
    check("victim_drops_before_attacker", [e["id"] for e in w.events if e["event"]=="death"]==[0,2])
    traces["bad_head_feed"] = w.events
    # Moving into a queen's body kills only donor, at its pre-contact location.
    w = World([straight(0,4), Dragon(2,0,((-1,1),(-1,2),(-1,3)))])
    w.move(2,[DIRS[0]])
    check("body_feed_preserves_queen", w.dragons[0].alive and not w.dragons[2].alive)
    check("body_feed_drops_before_contact", (-1,1) in w.pearls and (-1,0) not in w.pearls)
    traces["body_feed"] = w.events
    # Wall and oversprint locations differ; oversprint reduces donation first.
    w = World([straight(2,5)], cells=set(straight(2,5).body))
    w.move(2,[DIRS[1]])
    check("wall_drops_at_original_body", len(w.pearls)==3 and (1,0) not in w.pearls)
    w = World([straight(2,5)])
    w.move(2,[DIRS[1]]*6)
    check("oversprint_drops_only_remaining_length2", len(w.pearls)==1 and (5,0) in w.pearls)
    traces["oversprint"] = w.events
    # Simple portal fixture shows coordinate distance isn't a safety bound.
    w = World([straight(0,3,(20,0)),straight(2,2)], portals={((0,0),DIRS[1]):(20,0)})
    w.move(2,[DIRS[1]])
    check("portal_one_step_far_head_attack", not w.dragons[0].alive)
    table("drops.csv", [dict(L=l,drops=(l+1)//2, efficiency=(l+1)//2/l)
                         for l in range(2,41)])
    feed = []
    for q in range(2,41):
        w = World([straight(0,q)], pearls=[(1,0),(3,0)])
        alive = w.move(0,[DIRS[1]]*3)
        feed.append(dict(Q=q,free=free(q),requested_steps=3,survives=alive,
                         collected=sum(e.get("ate",False) for e in w.events),
                         final_length=len(w.dragons[0].body) if alive else 0,
                         net_length=len(w.dragons[0].body)-q if alive else "DEAD"))
    table("L3-stream.csv", feed)
    w = World([straight(0,9)])
    pipeline=[]
    for turn in range(1,11):
        h=w.dragons[0].body[0][0]
        ident=turn+1
        w.dragons[ident]=Dragon(ident,0,((h+1,0),(h+2,0),(h+3,0)))
        w.move(ident,[DIRS[1]])
        w.move(0,[DIRS[1]]*3)
        pipeline.append(dict(delivery=turn,queen_length=len(w.dragons[0].body),head=w.dragons[0].body[0]))
    check("ten_L3_deliveries_gain20", len(w.dragons[0].body)==29)
    traces["pipeline_assumes_each_donor_already_staged_after_queen_previous_turn"] = pipeline
    split_attacks=[]
    for length in range(4,41):
        c=length-2; distance=length-1+maximum(c)
        enemy=Dragon(2,1,tuple((i,0) for i in range(length)))
        queen=Dragon(0,0,((distance,0),(distance+1,0),(distance+2,0)))
        w=World([queen,enemy]); child=w.split(2,c)
        assert child==3
        w.move(child,[DIRS[1]]*maximum(c))
        check(f"L{length}_split_child_attacks_at_distance_{distance}",not w.dragons[0].alive and w.dragons[2].alive)
        split_attacks.append(dict(L=length,queen=queen.body,enemy=enemy.body,
                                 split_size=c,child_id=child,child_move='E'*maximum(c),
                                 head_distance=distance,events=w.events))
    traces['split_child_assassination_tight_distance_witnesses']=split_attacks
    two_split=[]
    for length in range(4,41):
        c=length-2; distance=length-1+2*free(c)+c-2
        enemy=Dragon(2,1,tuple((i,0) for i in range(length)))
        queen=Dragon(0,0,((distance,0),(distance+1,0),(distance+2,0)))
        w=World([queen,enemy]); child=w.split(2,c)
        first='E'*free(c); second='E'*maximum(c)
        assert w.move(child,[DIRS[1]]*free(c))
        # Root parent must also act in round 2; a west step preserves it.
        assert w.move(2,[DIRS[3]])
        assert not w.move(child,[DIRS[1]]*maximum(c))
        assert not w.dragons[0].alive
        two_split.append(dict(L=length,queen=queen.body,enemy=enemy.body,
                              split_size=c,first_child_move=first,second_child_move=second,
                              second_parent_move='W',head_distance=distance,events=w.events))
    traces['two_turn_split_family_tight_old_target_witnesses']=two_split
    # Exact r500 lexicographic score, no queen succession.
    check("living_short_queen_beats_dead_queen_huge_backup", score([2,0],[[2],[100]])[0]>score([2,0],[[2],[100]])[1])
    check("both_dead_backup_longest_precedes_total", score([0,0],[[9],[8,8]])[0]>score([0,0],[[9],[8,8]])[1])
    dump("fixtures.json",traces)
    return checks

def paths(cells,length):
    def dfs(path):
        if len(path)==length:
            yield tuple(path)
            return
        for d in DIRS:
            dest=add(path[-1],d)
            if dest in cells and dest not in path:
                yield from dfs(path+[dest])
    for p in sorted(cells):
        yield from dfs([p])

def viability(cells,length):
    """Exact greatest fixed point for constant-length no-pearl one-step motion.

    Delete states without successors, recursively. All survivors have an infinite
    legal one-step strategy. No threat assumptions are included in this result.
    """
    states=list(paths(cells,length))
    index={s:i for i,s in enumerate(states)}
    succ=[[] for _ in states]
    pred=[[] for _ in states]
    for i,body in enumerate(states):
        for d in DIRS:
            dest=add(body[0],d)
            if dest in cells and dest not in body:
                j=index[(dest,)+body[:-1]]
                succ[i].append(j)
                pred[j].append(i)
    degree=[len(x) for x in succ]
    dead={i for i,n in enumerate(degree) if n==0}
    queue=deque(dead)
    while queue:
        j=queue.popleft()
        for i in pred[j]:
            if i in dead:
                continue
            degree[i]-=1
            if degree[i]==0:
                dead.add(i); queue.append(i)
    safe=set(range(len(states)))-dead
    witness=None
    if safe:
        i=min(safe); seen={}; trace=[]
        while i not in seen:
            seen[i]=len(trace); trace.append(states[i])
            i=next(j for j in succ[i] if j in safe)
        witness=dict(transient=trace[:seen[i]],period=trace[seen[i]:])
    return len(states),len(safe),witness

def canonical(cells):
    variants=[]
    for swap in (False,True):
        for sx in (-1,1):
            for sy in (-1,1):
                points=[(sx*(y if swap else x),sy*(x if swap else y)) for x,y in cells]
                mx=min(x for x,y in points); my=min(y for x,y in points)
                variants.append(tuple(sorted((x-mx,y-my) for x,y in points)))
    return min(variants)

def connected(cells):
    if not cells:return False
    seen={next(iter(cells))}; queue=list(seen)
    for p in queue:
        for d in DIRS:
            v=add(p,d)
            if v in cells and v not in seen:
                seen.add(v); queue.append(v)
    return seen==cells

def longest_cycle(cells):
    # A DFS exact simple-cycle search, fixed smallest vertex eliminates rotation.
    best=()
    def dfs(start,path,seen):
        nonlocal best
        for d in DIRS:
            v=add(path[-1],d)
            if v==start and len(path)>=4:
                if len(path)>len(best):best=tuple(path)
            elif v in cells and v not in seen and v>start:
                dfs(start,path+[v],seen|{v})
    for p in sorted(cells):dfs(p,[p],{p})
    return best

def rectangle_cycle(width,height):
    if width%2==0:
        out=[(0,0)]
        for x in range(width):
            ys=range(1,height) if x%2==0 else range(height-1,0,-1)
            out.extend((x,y) for y in ys)
        out.extend((x,0) for x in range(width-1,0,-1))
        return tuple(out)
    if height%2==0:
        return tuple((y,x) for x,y in rectangle_cycle(height,width))
    # Odd x odd: even-width strip plus disjoint two-tile detours along its
    # right border. All tiles except bottom-right are included.
    base=rectangle_cycle(width-1,height); out=[]
    for i,p in enumerate(base):
        out.append(p); nxt=base[(i+1)%len(base)]
        if p[0]==nxt[0]==width-2 and abs(p[1]-nxt[1])==1 and min(p[1],nxt[1])%2==0:
            out.extend(((width-1,p[1]),(width-1,nxt[1])))
    return tuple(out)

def draw(cells,body=()):
    w=max(x for x,y in cells)+1; h=max(y for x,y in cells)+1
    parts={p:("H" if i==0 else "t" if i==len(body)-1 else "q") for i,p in enumerate(body)}
    return "\n".join("".join(parts.get((x,y),"." if (x,y) in cells else "#") for x in range(w)) for y in range(h))

def enumerate_rooms():
    full={(x,y) for x in range(3) for y in range(3)}
    records=[]; pictures=[]; cycles={}
    for mask in range(1,512):
        cells={p for i,p in enumerate(sorted(full)) if mask>>i&1}
        if not connected(cells):continue
        canon=canonical(cells)
        if canon not in cycles:cycles[canon]=longest_cycle(set(canon))
        cycle=cycles[canon]
        for length in range(2,min(8,len(cells))+1):
            total,safe,witness=viability(cells,length)
            # On these fully enumerated masks, viability agrees with large cycle.
            assert bool(safe)==(len(cycle)>length),(mask,length,len(cycle),safe)
            records.append(dict(mask=mask,cells=sorted(cells),L=length,
                                states=total,safe_states=safe,
                                max_cycle=len(cycle),witness=witness))
    dump("rooms-3x3.json",dict(scope="all connected induced tile masks of 3x3; every ordered simple body L=2..min(8,area); no pearls/hunters/splits/paid shrink",records=records))
    # Print all symmetry-distinct safe shapes, with exactly one witness per L.
    seen=set()
    for r in records:
        if not r["safe_states"]:continue
        key=canonical({tuple(p) for p in r["cells"]}),r["L"]
        if key in seen:continue
        seen.add(key)
        cells=set(key[0]); total,safe,witness=viability(cells,r["L"])
        body=witness["period"][0]
        pictures.append(f"shape={len(seen)} L={r['L']} area={len(cells)} states={total} viable={safe} period={len(witness['period'])}\n{draw(cells,body)}\n")
    (OUT/"rooms-pictures.txt").write_text("\n".join(pictures)+"\n")
    rect=[]
    for width in range(1,5):
        for height in range(width,5):
            cells={(x,y) for x in range(width) for y in range(height)}
            cycle=longest_cycle(cells)
            formula=0 if width==1 else width*height-(width*height%2)
            assert len(cycle)==formula
            rect.append(dict(width=width,height=height,area=len(cells),
                             max_cycle=len(cycle),max_constant_queen=max(0,len(cycle)-1),
                             witness=cycle))
    dump("rectangles.json",rect)
    constructed=[]
    for width in range(2,11):
        for height in range(2,11):
            cycle=rectangle_cycle(width,height)
            assert len(set(cycle))==len(cycle)==width*height-width*height%2
            assert all(abs(a[0]-b[0])+abs(a[1]-b[1])==1 for a,b in zip(cycle,cycle[1:]+cycle[:1]))
            q=len(cycle)-1
            body=tuple(cycle[-i%len(cycle)] for i in range(q))
            w=World([Dragon(0,0,body)],cells={(x,y) for x in range(width) for y in range(height)})
            for i in range(2*len(cycle)):
                a=cycle[i%len(cycle)]; b=cycle[(i+1)%len(cycle)]
                assert w.move(0,[(b[0]-a[0],b[1]-a[1])])
                assert len(w.dragons[0].body)==q
            constructed.append(dict(width=width,height=height,cycle=cycle,queen_length=q,verified_steps=2*len(cycle)))
    dump("rectangle-constructions.json",constructed)
    table("cycle.csv",[dict(L=l,min_planar_cycle=max(4,2*((l+2)//2)),
                             min_general_graph_cycle=l+1) for l in range(2,41)])
    return dict(masks=len({r['mask'] for r in records}),mask_length_cases=len(records),
                body_states=sum(r['states'] for r in records),
                viable_states=sum(r['safe_states'] for r in records),
                symmetry_distinct_safe_shape_length_cases=len(seen))

def assassination():
    # Exact all queen MOVE prefixes + all legal splits; hunters see final state.
    fixtures=[
        ("open_Q2_H2_one",None,straight(0,2),[Dragon(2,1,((1,-1),(2,-1)))]),
        ("open_Q2_H2_two",None,straight(0,2),[Dragon(2,1,((1,-1),(2,-1))),Dragon(3,1,((1,1),(2,1)))]),
        ("corridor_Q3_H3",{(x,0) for x in range(-3,8)},straight(0,3),[Dragon(2,1,((3,0),(4,0),(5,0)))]),
        ("corridor_Q4_H2",{(x,0) for x in range(-4,9)},straight(0,4),[Dragon(2,1,((4,0),(5,0)))]),
        ("mouth_Q3_H3",{(-2,0),(-1,0),(0,0),(1,0),(2,0),(2,1),(2,2)},straight(0,3),[Dragon(2,1,((2,0),(2,1),(2,2)))]),
        ("open_Q2_H4_one",None,straight(0,2),[Dragon(2,1,((1,-1),(2,-1),(3,-1),(4,-1)))]),
        ("open_Q3_H5_one",None,straight(0,3),[Dragon(2,1,((1,-1),(2,-1),(3,-1),(4,-1),(5,-1)))]),
        ("open_Q3_H6_one",None,straight(0,3),[Dragon(2,1,((1,-1),(2,-1),(3,-1),(4,-1),(5,-1),(6,-1)))]),
    ]
    output=[]
    for name,cells,q,hunters in fixtures:
        initial=World([q]+hunters,cells)
        choices=move_states(initial,0)
        for size in range(2,len(q.body)-1):
            w=initial.clone(); w.split(0,size)
            choices.append((w,"SPLIT "+str(size)))
        cases=[]
        for w,action in choices:
            wins=[]
            # Replay one actual response in ascending id order. If an earlier
            # hunter cannot kill, choose a living action that allows a later kill.
            def response(state,index):
                if not state.dragons[0].alive:return []
                if index==len(hunters):return None
                hid=hunters[index].ident
                if not state.dragons[hid].alive:return response(state,index+1)
                path=attack_path(state,hid,0)
                if path is not None:return [(hid,path)]
                for later,move in move_states(state,hid,include_kills=True):
                    found=response(later,index+1)
                    if found is not None:return [(hid,move)]+found
                return None
            found=response(w,0)
            if found is None and len(hunters)==1:
                # A negative MOVE result is not an escape until all recursive
                # same-round SPLIT descendants have also been ruled out.
                assert family_attack_actions(w,hunters[0].ident,0) is None,(name,action)
            if found is not None:
                verify=w.clone()
                for hid,path in found:
                    verify.move(hid,[DIRS[LETTERS.index(c)] for c in path])
                assert not verify.dragons[0].alive
            cases.append(dict(queen_action=action,queen_body=w.dragons[0].body,
                              forced_contact=found is not None,hunter_response=found))
        output.append(dict(name=name,cells=None if cells is None else sorted(cells),
                           queen=q.body,hunters=[dict(id=h.ident,body=h.body) for h in hunters],
                           legal_queen_choices=len(cases),
                           negative_cases_include_recursive_hunter_splits=True,
                           all_choices_killed=bool(cases) and all(c['forced_contact'] for c in cases),cases=cases))
    assert not output[0]['all_choices_killed']
    assert output[1]['all_choices_killed']
    assert output[2]['all_choices_killed']
    assert not output[3]['all_choices_killed'] # third initial step toward queen too far
    assert output[4]['all_choices_killed']
    assert output[5]['all_choices_killed']
    assert output[7]['all_choices_killed']
    # Exhaust every possible one length-2 hunter that can touch a Q2 endpoint
    # in one step. Farther heads cannot cover ANY endpoint; bodies matter too.
    q=straight(0,2); count=0; force=[]
    for head in sorted(diamond(2)-set(q.body)):
        for d in DIRS:
            body=(head,add(head,d))
            if set(body)&set(q.body):continue
            count+=1
            w=World([q,Dragon(2,1,body)])
            choices=move_states(w,0)
            if choices and all(attack_path(state,2,0) is not None for state,_ in choices):
                force.append(body)
    assert not force
    dump("assassination.json",dict(fixtures=output,Q2_H2_one_hunter_exhaust=dict(configurations=count,forcing_configurations=force,
          completeness="Hunter head must be within distance 2 of queen start to hit a one-step endpoint; all four length2 body headings included. No split legal for Q2.")))
    return output

def vaults():
    """Enumerate cycle phases whose endpoint mouth is a NON-head body tile.

    External attackers have exactly one entry tile (gate index 0), no portal,
    and start outside. Any attack then meets BODY, never the queen's head.
    Queen uses only free moves and receives no growth. This is a sufficient
    invariant, not a claim that every other vault strategy is impossible.
    """
    rows=[]; witnesses=[]
    for q in range(2,41):
        for c in range(4,51,2):
            if c<=q:continue
            gap=c-q
            allowed={h for h in range(c) if 0 in {(h-j)%c for j in range(1,q)}}
            succ={h:[(h+n)%c for n in range(1,free(q)+1)
                     if (h+n)%c in allowed] for h in allowed}
            safe=set(allowed)
            while True:
                nxt={h for h in safe if any(j in safe for j in succ[h])}
                if nxt==safe:break
                safe=nxt
            formula=free(q)>=gap+2
            assert bool(safe)==formula
            rows.append(dict(Q=q,C=c,gap=gap,free=free(q),required_jump=gap+2,
                             perpetual_body_gate=bool(safe),safe_phases=len(safe)))
            if safe:
                h=min(safe); seen={}; trace=[]
                while h not in seen:
                    seen[h]=len(trace)
                    n=next(n for n in range(1,free(q)+1) if (h+n)%c in safe)
                    trace.append(dict(head_phase=h,steps=n)); h=(h+n)%c
                witnesses.append(dict(Q=q,C=c,period=trace[seen[h]:]))
    table("vault-phases.csv",rows); dump("vault-witnesses.json",witnesses)
    pictures=[]
    for witness in witnesses:
        q,c=witness['Q'],witness['C']; width=c//2
        cycle=tuple([(x,0) for x in range(width)]+[(x,1) for x in range(width-1,-1,-1)])
        phase=witness['period'][0]['head_phase']
        body=tuple(cycle[(phase-i)%c] for i in range(q))
        assert cycle[0] in body[1:]
        pictures.append(f"Q={q} C={c} room=2x{width} gate=(0,0) external entrance left of top-left; no-growth/free-move invariant\n{draw(set(cycle),body)}\nsteps={','.join(str(x['steps']) for x in witness['period'])}\n")
    (OUT/'vault-pictures.txt').write_text('\n'.join(pictures)+'\n')
    # Real 2x5 room, Q9: all 8 allowed starting phases, repeated 20 cycles.
    cycle=tuple([(x,0) for x in range(5)]+[(x,1) for x in range(4,-1,-1)])
    cells=set(cycle)|{(-1,0),(-2,0),(-3,0)}
    traces=[]
    for start in range(1,9):
        body=tuple(cycle[(start-i)%10] for i in range(9))
        w=World([Dragon(0,0,body),Dragon(2,1,((-1,0),(-2,0)))],cells)
        steps=[]; phase=start
        for turn in range(160):
            n=3 if phase==8 else 1
            dests=[cycle[(phase+j)%10] for j in range(1,n+1)]
            dirs=[]; pos=w.dragons[0].body[0]
            for dest in dests:
                dirs.append((dest[0]-pos[0],dest[1]-pos[1])); pos=dest
            assert w.move(0,dirs)
            phase=(phase+n)%10
            assert cycle[0] in w.dragons[0].body[1:]
            assert len(w.dragons[0].body)==9
            assert attack_path(w,2,0) is None
            steps.append(n)
        traces.append(dict(start_phase=start,turns=len(steps),step_word=steps[:8]))
    # Unguarded C4/Q3 cycle: head exposed at gate; H2 kills in one step.
    small=((0,0),(1,0),(1,1),(0,1))
    w=World([Dragon(0,0,(small[0],small[3],small[2])),Dragon(2,1,((-1,0),(-2,0)))],set(small)|{(-1,0),(-2,0)})
    assert attack_path(w,2,0)=="E"
    # Growth can destroy even the strongest no-growth vault: one pearl in its
    # sole gap fills C10 and the next substep tries to enter the old tail.
    body=tuple(cycle[(8-i)%10] for i in range(9))
    grown=World([Dragon(0,0,body)],cells,pearls=[cycle[9]])
    assert not grown.move(0,[DIRS[3],DIRS[0],DIRS[1]])
    assert grown.events[-1]['reason']=='Hit Self'
    dump("vault-growth-counterexample.json",dict(Q=9,C=10,start_body=body,
         pearl=cycle[9],requested_move="WNE",events=grown.events,
         explanation="first free step eats and fills cycle; second step's destination is own tail before advance"))
    dump("vault-verification.json",dict(phase_cases=len(rows),body_gate_safe_cases=sum(r['perpetual_body_gate'] for r in rows),
                Q9_C10_all_allowed_phases=traces,
                unguarded_Q3_C4_head_exposure_attack="E",
                strong_invariant="gate tile is queen NON-head body after EVERY queen action; no other ingress/portal; no growth/shrink; attackers initially outside",
                growth_counterexample="vault-growth-counterexample.json"))
    # Minimal-cycle designs, including parity-induced gaps of 1 or 2.
    table("vault-minimal.csv",[dict(Q=q,C=max(4,2*((q+2)//2)),free=free(q),
          gap=max(4,2*((q+2)//2))-q,
          body_gate_possible=free(q)>=max(4,2*((q+2)//2))-q+2) for q in range(2,41)])
    return dict(phase_cases=len(rows),safe_cases=sum(r['perpetual_body_gate'] for r in rows),Q9_fixture_turns=1280)

def backup_model():
    # Utility win=1, draw=.5, loss=0, at r500 with nonempty teams assured.
    # s = opponent queen survival. a/b = conditional queen-comparison utility.
    # t = conditional utility when both queens dead. p may differ by policy.
    def ev(p,s,a,t):return p*(1-s+s*a)+(1-p)*(1-s)*t
    scenarios=[dict(name="equal_survival",p_feed=p,p_backup=p,s=.8,a_feed=.8,a_backup=.6,t_feed=.2,t_backup=.9)
               for p in (0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1)]
    rows=[]
    for x in scenarios:
        uf=ev(x['p_feed'],x['s'],x['a_feed'],x['t_feed'])
        ub=ev(x['p_backup'],x['s'],x['a_backup'],x['t_backup'])
        rows.append(dict(p=x['p_feed'],opponent_survival=x['s'],feed_EV=uf,
                         backup_EV=ub,backup_minus_feed=ub-uf))
    table("backup-EV.csv",rows)
    dump("backup-model.json",dict(utility="win=1 draw=.5 loss=0; r500; both teams retain at least one survivor; conditional comparisons abstract all tie levels",formula="U=p*(1-s+s*a)+(1-p)*(1-s)*t",
          assumptions=dict(s=.8,a_feed=.8,a_backup=.6,t_feed=.2,t_backup=.9,
                           independent_queen_survival=True,p_same_for_both_policies=True),
          threshold=(.2*.7)/(.8*.2+.2*.7),
          generalized_formula="U(policy)=p_policy*(1-s+s*a_policy)+(1-p_policy)*(1-s)*t_policy",
          correlated_formula="U=P(ours alive,enemy dead)+P(both alive)*a+P(both dead)*t"))
    # A second model derives a,t from concrete lengths and ALL three tiebreaks.
    # Base queen14, worker2 always remains. Either retain donor3 or transfer
    # its two drops to queen16. Enemy has queen U{10..20}, backup U{2,3,4}.
    def utility(keys):
        return 1.0 if keys[0]>keys[1] else .5 if keys[0]==keys[1] else 0.0
    policies={"feed":(16,[2]),"backup":(14,[3,2])}
    terms={}; cases=[]
    for policy,(q,workers) in policies.items():
        alive=[]; dead=[]
        for eq in range(10,21):
            for eb in range(2,5):
                keys=score([q,eq],[[q]+workers,[eq,eb]])
                alive.append(utility(keys))
                cases.append(dict(policy=policy,our_queen=q,enemy_queen=eq,enemy_backup=eb,
                                  both_alive_keys=keys,utility=utility(keys)))
        for eb in range(2,5):
            dead.append(utility(score([0,0],[workers,[eb]])))
        terms[policy]=dict(a=sum(alive)/len(alive),t=sum(dead)/len(dead))
    delta_a=terms['feed']['a']-terms['backup']['a']
    delta_t=terms['backup']['t']-terms['feed']['t']
    threshold=.2*delta_t/(.8*delta_a+.2*delta_t)
    concrete=[]
    for p in (0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1):
        uf=ev(p,.8,**terms['feed']); ub=ev(p,.8,**terms['backup'])
        concrete.append(dict(p=p,feed_EV=uf,backup_EV=ub,backup_minus_feed=ub-uf))
    table("backup-concrete.csv",concrete)
    dump("backup-concrete.json",dict(assumptions="ours queen14+L3 donor+L2 worker; feed gives queen16+worker2; backup gives queen14+workers3,2; enemy queen uniform integer10..20 and one backup uniform2..4; enemy survival s=.8; p same by policy; independent survivals; terminal lengths fixed conditional on survival; illustrative distributions, NOT predictions",terms=terms,threshold=threshold,both_alive_score_cases=cases))
    # Literal feed-EVERYTHING: same starting Q14+L3+L2. F feeds both donors
    # -> Q17 alone; B feeds L2 -> Q15 + backup3. If F queen dies, early
    # elimination means loss regardless of enemy queen's later fate.
    af=sum(utility(score([17,eq],[[17],[eq,eb]]))
           for eq in range(10,21) for eb in range(2,5))/33
    ab=sum(utility(score([15,eq],[[15,3],[eq,eb]]))
           for eq in range(10,21) for eb in range(2,5))/33
    tb=sum(utility(score([0,0],[[3],[eb]])) for eb in range(2,5))/3
    literal=[]
    for p in (0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1):
        uf=p*(.2+.8*af); ub=p*(.2+.8*ab)+(1-p)*.2*tb
        literal.append(dict(p=p,feed_everything_EV=uf,keep_L3_EV=ub,backup_minus_feed=ub-uf))
    table("backup-feed-everything.csv",literal)
    dump("backup-feed-everything.json",dict(starting_lengths=[14,3,2],feed_everything=[17],keep_backup=[15,3],
          assumptions="Same enemy length distributions/s=.8 as concrete model; p same by policy, independent; full drop collection free; enemy always has living backup2..4. Feed-all queen death is early team elimination and loss.",
          a_feed=af,a_backup=ab,t_backup=tb,
          feed_formula="U_F=39p/55",backup_formula="U_B=1/10+p/2",threshold=11/23))

def main():
    sources=['movement','execution-order','splitting','death','structure','vision','sonar','ALL','pearls','kelp-and-portals','map-info','map-files','protocol','timeouts']
    dump("source-manifest.json",{f'rules/{s}.md':hashlib.sha256((ROOT/'rules'/f'{s}.md').read_bytes()).hexdigest() for s in sources})
    rows=reach_tables(); print("reach complete",flush=True)
    checks=checks_and_feeding(); print("fixtures complete",flush=True)
    rooms=enumerate_rooms(); print("rooms complete",rooms,flush=True)
    attacks=assassination(); print("assassination complete",flush=True)
    vault=vaults(); print("vault complete",vault,flush=True)
    backup_model()
    dump("verification.json",dict(assertions_passed=True,fixture_checks=checks,rooms=rooms,
          reach_lengths=len(rows),exact_reach_lengths=7,vault=vault,
          assassination=[dict(name=a['name'],legal_queen_choices=a['legal_queen_choices'],all_choices_killed=a['all_choices_killed']) for a in attacks]))
    print("all assertions passed",flush=True)

if __name__=='__main__':main()

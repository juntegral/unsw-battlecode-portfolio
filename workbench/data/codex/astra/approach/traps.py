"""Join existing EAT_FIRST trace decisions to their exact replay geometries.
No bot execution. Exhaustive body-state search, with a finite state cap.
"""
import sys, json, re
sys.dont_write_bytecode=True
from scan import Board, OUT, RUNS
from collections import defaultdict, Counter
from pathlib import Path

TRACE=Path.home()/'meow-redteam/solo/src/w-eat/tr'

def escape(B, body, target, pearls, other, cap=50000):
    # Collision is checked against the current body, including its tail.
    initial=(target,)+tuple(body)
    horizon=len(initial)+2
    memo=set(); visits=0
    def dfs(b,food,left):
        nonlocal visits
        if left==0: return []
        key=(b,food,left)
        if key in memo: return None
        visits+=1
        if visits>cap: raise OverflowError
        memo.add(key)
        for d,n in enumerate(B.adj[b[0]]):
            if n is None or n in b or n in other: continue
            grow=n in food
            nb=(n,)+b if grow else (n,)+b[:-1]
            found=dfs(nb,food-{n} if grow else food,left-1)
            if found is not None: return [d]+found
        return None
    try:
        path=dfs(initial,frozenset(pearls)-{target},horizon)
        return dict(status='escape' if path is not None else 'trap',path=path,states=visits,horizon=horizon)
    except (OverflowError,RecursionError):
        return dict(status='unknown',path=None,states=visits,horizon=horizon)

def trace_cases(path):
    pending=defaultdict(list); cases={}; reasons=Counter()
    for line in path.open():
        if not line.startswith(('PEARL ','DID ')): continue
        d=dict(re.findall(r'(\w+)=([^ ]+)',line.strip()))
        key=(int(d['r']),int(d['id']))
        if line.startswith('PEARL '): pending[key].append(d); continue
        ps=pending.pop(key,[])
        if not ps or ps[0]['queen']=='1': continue
        if any(p['chosen']=='1' for p in ps):
            reasons['picked_split' if d['split']!='0' else 'picked']+=1; continue
        if d['split']!='0': reasons['other_split']+=1; continue
        dead=[p for p in ps if p['scored']=='1' and p['dead']=='1']
        if dead:
            reasons['refused_dead_turns']+=1
            cases[key]=dead
        else: reasons['other_refusal']+=1
    return cases,dict(reasons)

def main():
    allrows=[]; inventory=[]
    for log in sorted(TRACE.glob('flip-*.log')):
        game=log.stem[5:]
        cases,reasons=trace_cases(log)
        B=Board(RUNS/'m9etr1'/game/'game.replay'); matched=set()
        for ev in B.root.pointer(3):
            k=ev.u16(0)
            if k not in (0,1,3,9,10,11): continue
            p=ev.pointer(0); B.update(k,p)
            key=(B.rnd,B.actor)
            if k!=1 or key not in cases: continue
            matched.add(key)
            body=tuple(B.bodies[B.actor]); other=set(c for i,b in B.bodies.items() if i!=B.actor for c in b)
            for tr in cases[key]:
                assert tuple(map(int,re.findall(r'-?\d+',tr['h'])))==body[0]
                assert int(tr['L'])==len(body)
                target=B.adj[body[0]][int(tr['k'])]
                assert target in B.pearls and target not in other and target not in body
                frozen=escape(B,body,target,B.pearls,other)
                optimistic=escape(B,body,target,B.pearls,set()) if frozen['status']!='escape' else frozen
                status='safe' if frozen['status']=='escape' else 'intrinsic_trap' if optimistic['status']=='trap' else 'occupied_exit' if optimistic['status']=='escape' else 'unknown'
                allrows.append(dict(game=game,r=B.rnd,i=B.actor,body=body,target=target,trace=tr,
                                    status=status,frozen=frozen,optimistic=optimistic,
                                    snapshot=B.snap()))
        inventory.append(dict(game=game,reasons=reasons,matched=len(matched),expected=len(cases)))
        assert len(matched)==len(cases)
    (OUT/'traps.json').write_text(json.dumps(dict(inventory=inventory,rows=allrows),separators=(',',':')))
    for window in ('early','all'):
        rs=[r for r in allrows if window=='all' or r['r']<=100]
        print(window,'candidate tiles',len(rs),dict(Counter(r['status'] for r in rs)),flush=True)
    print(inventory)

if __name__=='__main__': main()

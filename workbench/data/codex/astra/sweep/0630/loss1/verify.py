import json
from analyze import Geo,OUT

results=[]
for gid in (1496845,1496846,1496847):
    g=json.loads((OUT/f'{gid}.json').read_text())
    assert g['bot']=='21269'
    q=g['queens'][0]
    qt=[t for t in g['qturns'] if t['id']==q][-1]
    geo=Geo(g['w'],g['h'],g['edges']);w=g['w']
    occ={y*w+x for b in qt['state'].values() for x,y in b}
    pearls={y*w+x for x,y in qt['pearls']}
    body=[y*w+x for x,y in qt['body']]
    endpoints=[]
    free=(len(qt['body'])+3)//4
    def walk(body,steps,path,ate=frozenset(),visited=frozenset()):
        if steps:
            target=body[0]
            attackers=[]
            for i,b in qt['state'].items():
                if g['teams'][i]!=1:continue
                ds=geo.ball(b[0][1]*w+b[0][0]).get(target,999)
                reach=(len(b)+3)//4+len(b)-2
                if ds<=reach:attackers.append([int(i),len(b),ds,reach])
            endpoints.append(dict(path=path,end=[target%w,target//w],length=len(body),
                                  terrain_reachable_without_eating=attackers))
        if steps>=6 or (steps>=free and len(body)<=2):return
        for d,n in enumerate(geo.nxt[body[0]]):
            if n<0 or n in occ or n in body or n in visited:continue
            hx,hy=qt['body'][0];x,y=n%w,n//w
            if min(abs(x-hx),w-abs(x-hx))>3 or min(abs(y-hy),g['h']-abs(y-hy))>3:continue
            eat=n in pearls and n not in ate
            new=[n]+body
            while len(new)>len(body)-(steps>=free)+eat:new.pop()
            walk(new,steps+1,path+'NESW'[d],ate|({n} if eat else set()),visited|{n})
    walk(body,0,'')
    snap=g['snapshots']
    last=max((int(r) for r,s in snap.items() if
              tuple(s['us'][k] for k in ('queen_length','longest','total'))>=
              tuple(s['them'][k] for k in ('queen_length','longest','total'))),default=-1)
    no_eat=[]
    for s in (0,1):
        ts=[t for t in g['turns'] if t['side']==s and 201<=t['r']<=300]
        no_eat.append(dict(turns=len(ts),move_no_eat=sum(t['action']==0 and not t['eats'] for t in ts),
                           move_eat=sum(t['action']==0 and bool(t['eats']) for t in ts),
                           split=sum(t['action']==1 for t in ts)))
    results.append(dict(gid=gid,permanent_behind_round=last+1,final_queen_turn_paths=endpoints,
                        turns_201_300=no_eat,
                        nearest_after_queen_death=min(g['post_near'],key=lambda r:r['d']) if g['post_near'] else None))
assert results[0]['nearest_after_queen_death']['d']==35
assert [r['permanent_behind_round'] for r in results]==[0,164,189]
ne=next(e for e in results[2]['final_queen_turn_paths'] if e['path']=='NE')
assert ne['end']==[14,24] and ne['length']==2 and not ne['terrain_reachable_without_eating']
output=dict(note='Endpoint reach is a frozen-state terrain bound using actual length, without future eating or other turns. It is not a counterfactual game.',games=results)
(OUT/'verification.json').write_text(json.dumps(output,ensure_ascii=False,indent=2))
print(json.dumps(output,ensure_ascii=False))

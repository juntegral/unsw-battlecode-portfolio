"""Bound the territory term in selected replay moments using personal 7x7
view history. This is a partial score reconstruction, not an execution trace.
Known-cell territory weights are bounded [0,1] because online spawn timers
are redacted. Unknown-cell weight is exactly 0.5. No portals in these cases.
"""
import sys,json
sys.dont_write_bytecode=True
from scan import Board,OUT,edge_id,STEP
from collections import deque

CASES=[('one4-w1','1470218',4,12),('one5-w1','1472005',25,23),('one5-d1','1471459',7,17),('one5-d1','1471470',98,22)]

def measure(label,game,actor,rnd):
    meta=json.loads((OUT/f'scan-{label}-{game}.json').read_text())['meta']
    B=Board(meta['path']); seen=set(); edges=set(); food=set(); observed=[]
    for ev in B.root.pointer(3):
        k=ev.u16(0)
        if k not in (0,1,3,9,10,11):continue
        p=ev.pointer(0);B.update(k,p)
        if k!=1 or B.actor!=actor:continue
        head=B.bodies[actor][0]
        visible={( (head[0]+dx)%B.W,(head[1]+dy)%B.H) for dx in range(-3,4) for dy in range(-3,4)}
        seen|=visible;food-=visible;food|=B.pearls&visible
        for c in visible:
            edges.update(edge_id(B.W,B.H,*c,d) for d in range(4))
        observed.append(B.rnd)
        if B.rnd==rnd:break
    assert B.rnd==rnd
    body=tuple(B.bodies[actor]);L=len(body)
    blocked={c for i,b in B.bodies.items() if i!=actor for c in b if c in visible}
    free={c:L-offset+1 for offset,c in enumerate(body)}
    def adj(c):
        for d,(dx,dy) in enumerate(STEP):
            e=edge_id(B.W,B.H,*c,d)
            kind=B.edges.get(e,(0,-1))[0] if e in edges else 0
            if kind==1:continue
            assert kind!=2, 'Portal knowledge unsupported by this diagnostic'
            yield ((c[0]+dx)%B.W,(c[1]+dy)%B.H)
    def rivals(heads):
        q=deque(heads);ds={h:0 for h in heads}
        while q:
            c=q.popleft()
            for n in adj(c):
                if n not in ds and n not in blocked and n not in free:
                    ds[n]=ds[c]+1;q.append(n)
        return ds
    mates=[b[0] for i,b in B.bodies.items() if i!=actor and B.teams[i]==meta['own'] and b[0] in visible]
    enemies=[b[0] for i,b in B.bodies.items() if B.teams[i]!=meta['own'] and b[0] in visible]
    ally=rivals(mates);enemy=rivals(enemies)
    result=[]
    for dest in adj(head):
        if dest in blocked or dest in free:continue
        q=deque([(dest,1,int(dest in food))]);visited={dest};ns=nu=os=ou=0;tail=False;dp=-1
        while q:
            c,t,eaten=q.popleft()
            theirs=enemy.get(c,10**9)
            share=1 if t<theirs else 0.5 if t==theirs else 0
            if ally.get(c,10**9)<t:share=0
            if c in seen:ns+=1;os+=share
            else:nu+=1;ou+=share
            tail|=c==body[-1]
            if dp<0 and c in food and (share==1 or (L<=4 and t<=theirs+1 and ally.get(c,10**9)>=t)):dp=t
            for n in adj(c):
                if n in visited or n in blocked or t+1-eaten<free.get(n,0):continue
                visited.add(n);q.append((n,t+1,eaten+int(n in food)))
        room=ns+0.5*nu;dead=not tail and room<3*L+8
        cramped=400*max(0,3*L+8-room)+5000*max(0,L+2-room)+(600 if not tail else 0)
        result.append(dict(dest=dest,room=room,tail=tail,dead=dead,cramped=cramped,dist_pearl=dp,
                           territory_min=ou*0.5,territory_max=ou*0.5+os,own_unseen=ou,own_seen_max=os))
    return dict(label=label,game=game,r=rnd,i=actor,head=head,L=L,mates=mates,enemies=enemies,
                observed_turns=observed,seen=len(seen),body=body,scores=result)

if __name__=='__main__':
    rows=[measure(*c) for c in CASES]
    (OUT/'territory.json').write_text(json.dumps(rows,indent=2))
    print(json.dumps(rows,indent=2))

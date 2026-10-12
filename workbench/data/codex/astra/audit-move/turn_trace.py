import sys
sys.dont_write_bytecode=True
import json
import audit as a

def trace(gid,lo,hi,ids):
    g=json.loads((a.OUT/f'game-{gid}.json').read_text());root=a.replay.load(g['path']).root()
    geo=a.Geo(root.text(0));bodies,teams=a.initial(root.text(0));pearls=set();r=-1;actor=None;rows=[];cur=None
    for e in root.pointer(3):
        k=e.u16(0)
        if k not in (0,1,3,4,9,10,11):continue
        p=e.pointer(0)
        if k==0:
            r=p.i32(0)
            if r>hi:break
        elif k==1:
            actor=p.i32(0);cur=None
            if lo<=r<=hi and actor in ids:
                b=bodies[actor];occ={c:i for i,bb in bodies.items() for c in bb};view={c for c in geo.adj if geo.visible(c,b[0])}
                cur=dict(r=r,id=actor,body=list(b),pearls=list(pearls&view),bodies={i:list(bb) for i,bb in bodies.items() if any(c in view for c in bb)},
                         options=[dict(dir=d,dest=n,owner=occ.get(n),next=geo.moves.get(n)) for d,n in enumerate(geo.moves[b[0]])],
                         edges={str(c):geo.moves[c] for c in view})
                rows.append(cur)
        elif k==3:
            c=a.replay.point(p.pointer(0))
            if p.u32(0):pearls.add(c)
            else:pearls.remove(c)
        elif k==4 and cur is not None:
            action=p.pointer(0);cur['action']=action.u16(0) if action else None
            cur['dirs']=list(action.pointer(0)) if action and action.u16(0)==0 and action.pointer(0) else []
        elif k==9:
            i=p.i32(0);hd=a.replay.point(p.pointer(0));tail=a.replay.point(p.pointer(1));b=bodies[i]
            if b[0]!=hd:b.appendleft(hd)
            while len(b)>1 and b[-1]!=tail:b.pop()
        elif k==10:
            for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=a.deque(a.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
        elif k==11:del bodies[p.i32(0)]
    (a.OUT/f'turns-{gid}.json').write_text(json.dumps(rows,indent=2))
    for t in rows:print(gid,t['r'],t['id'],t['body'],t.get('action'),t.get('dirs'),t['options'])

if __name__=='__main__':
    trace(1489831,130,138,{8})
    trace(1483009,39,43,{20,24})

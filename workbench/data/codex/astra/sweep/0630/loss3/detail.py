import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json
from collections import deque,Counter
ROOT=Path.cwd(); OUT=ROOT/'data/codex/astra/sweep/0630/loss3'
sys.path.insert(0,str(ROOT/'tools'))
import ladder_replay as lr

(OUT/'boards.txt').write_text('')
for gid in (1496851,1496852,1496857):
    root=lr.replay.load(ROOT/f'data/online/smoke/one11-c1-old/M{gid}.replay').root()
    W,H=map(int,root.text(0).splitlines()[0].split()[1:3])
    bodies={}; teams={}; edges=[]
    for line in root.text(0).splitlines():
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies); bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2]))); teams[i]=int(q[1])
        elif q and q[0]=='EDGE': edges.append(tuple(map(int,q[1:4])))
    edges=lr.canonical_edges(W,H,edges)
    queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
    def man(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1]);return min(dx,W-dx)+min(dy,H-dy)
    def view(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1]);return min(dx,W-dx)<=3 and min(dy,H-dy)<=3
    turns=[]; splits=[]; snaps={}; pearls=set(); rnd=-1; cur=None
    def snapshot():
        return {i:dict(side=teams[i],body=list(b)) for i,b in bodies.items()}
    def finish():
        if cur is not None: cur['end']=list(bodies.get(cur['id'],()))
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:
            finish()
            if rnd>=0: snaps[rnd]=snapshot()
            rnd=p.i32(0);cur=None
        elif k==1:
            finish();i=p.i32(0); b=bodies[i]
            cur=dict(r=rnd,event=idx,id=i,side=teams[i],L=len(b),start=list(b),moves=[],eats=[],action=None,split=False)
            occupied={c for bb in bodies.values() for c in bb}
            cur['adjacent_plain_pearls']=[((b[0][0]+dx)%W,(b[0][1]+dy)%H) for di,(dx,dy) in enumerate(lr.base.STEP) if edges.get(lr.edge_id(W,H,*b[0],di),(0,0))[0]==0 and ((b[0][0]+dx)%W,(b[0][1]+dy)%H) in pearls and ((b[0][0]+dx)%W,(b[0][1]+dy)%H) not in occupied]
            if i in queens:
                cur['state']=snapshot();cur['pearls']=list(pearls)
            cur['heads']={j:[teams[j],len(bb),bb[0]] for j,bb in bodies.items() if view(b[0],bb[0])}
            turns.append(cur)
        elif k==3:
            pt=lr.replay.point(p.pointer(0))
            if p.u32(0): pearls.add(pt)
            else: pearls.remove(pt);cur['eats'].append(pt)
        elif k==4:
            a=p.pointer(0);cur['action']={'type':a.u16(0),'dirs':list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else [],'data':a.i32(4)}
        elif k==9:
            i=p.i32(0);hd,tail=lr.replay.point(p.pointer(0)),lr.replay.point(p.pointer(1)); b=bodies[i]
            if b[0]!=hd:
                b.appendleft(hd);cur['moves'].append(hd)
            while len(b)>1 and b[-1]!=tail: b.pop()
            assert b[-1]==tail
        elif k==10:
            parent,child=p.i32(0),p.i32(4);before=list(bodies[parent]);cur['split']=True
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(lr.replay.point(pt) for pt in p.pointer(z)); teams[i]=p.u16(8)
            splits.append(dict(r=rnd,parent=parent,child=child,side=teams[parent],before=before,after=[list(bodies[parent]),list(bodies[child])]))
        elif k==11:
            cur.setdefault('deaths',[]).append([p.i32(0),p.u16(4),list(bodies[p.i32(0)])]);bodies.pop(p.i32(0))
    finish();snaps[rnd]=snapshot()
    (OUT/f'{gid}-detail.json').write_text(json.dumps(dict(W=W,H=H,queens=queens,turns=turns,splits=splits,snaps=snaps),separators=(',',':')))
    scan=json.loads((OUT/f'{gid}-scan.json').read_text())
    print('\nGAME',gid,'queens',queens)
    for field in ('queen_length','longest','total'):
        ss=scan['snapshots']; last_nonloss=max((int(r) for r,v in ss.items() if v['us'][field]>=v['them'][field]),default=-1)
        print('permanent strict deficit',field,last_nonloss+1)
    for d in scan['deaths']:
        if d['id']==queens[0]:
            last=[t for t in turns if t['id']==queens[0]][-3:]
            print('LAST QUEEN TURNS', [{k:v for k,v in t.items() if k not in ('state','pearls')} for t in last])
            atk=next(t for t in turns if t['event']<=d['event'] and t.get('deaths') and any(dd[0]==queens[0] for dd in t['deaths']))
            print('ATTACKER',atk)
            for t in last:
                center=t['start'][0]; occ={tuple(pt):('Q' if j==queens[0] and z==0 else 'q' if j==queens[0] else ('A' if v['side']==0 else 'E') if z==0 else ('a' if v['side']==0 else 'e')) for js,v in t['state'].items() for j in [int(js)] for z,pt in enumerate(v['body'])}
                title=f"{gid} r{t['r']} Q#{queens[0]} center={center} action={t['action']} moves={t['moves']}"
                lines=[title]
                for dy in range(-3,4):
                    y=(center[1]+dy)%H
                    wall=[];row=[]
                    for dx in range(-3,4):
                        x=(center[0]+dx)%W
                        wall.append('+'+('  ','--','::')[edges.get(lr.edge_id(W,H,x,y,0),(0,0))[0]])
                        row.append((' ','|',':')[edges.get(lr.edge_id(W,H,x,y,3),(0,0))[0]]+occ.get((x,y),'*' if (x,y) in set(map(tuple,t['pearls'])) else '.')+' ')
                    lines.extend([''.join(wall)+'+',''.join(row)+(' ','|',':')[edges.get(lr.edge_id(W,H,x,y,1),(0,0))[0]]])
                lines.append(''.join('+'+('  ','--','::')[edges.get(lr.edge_id(W,H,(center[0]+dx)%W,y,2),(0,0))[0]] for dx in range(-3,4))+'+')
                lines.append('heads '+str({j:v for j,v in t['heads'].items()}))
                with (OUT/'boards.txt').open('a') as f:f.write('\n'.join(lines)+'\n\n')
    print('QUEEN SPLITS', [s for s in splits if s['parent'] in queens])
    print('LONG DEATHS', [{k:d[k] for k in ('round','id','length','cause','actor','destination')} for d in scan['deaths'] if d['side']=='us' and d['length']>=8])
    print('FINAL',snapshot())

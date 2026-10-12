import sys
sys.dont_write_bytecode=True
import json,importlib.util
from pathlib import Path
from collections import Counter,deque
sys.path.insert(0,'tools')
import ladder_replay as lr
spec=importlib.util.spec_from_file_location('codec','../battlecode/work/card_42_check.py')
codec=importlib.util.module_from_spec(spec);spec.loader.exec_module(codec)
spec=importlib.util.spec_from_file_location('task',Path(__file__).with_name('analyze.py'))
task=importlib.util.module_from_spec(spec);spec.loader.exec_module(task)
OUT=Path(__file__).resolve().parent
rows=[]
for gid,folder,bot,side in task.JOBS:
    root=lr.replay.load(Path(folder)/f'M{gid}.replay').root()
    w,h=map(int,root.text(0).splitlines()[0].split()[1:3]);own='AB'.index(side)
    bodies,teams,edges0={},{},[]
    for line in root.text(0).splitlines():
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(q[1])
        elif q and q[0]=='EDGE':edges0.append(tuple(map(int,q[1:4])))
    queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)];uq=queens[own]
    edges=lr.canonical_edges(w,h,edges0);pairs={}
    for e,(k,p) in edges.items():
        if k==2:pairs.setdefault(p,[]).append(e)
    def dest(c,d):
        e=lr.edge_id(w,h,*c,d);k,p=edges.get(e,(0,-1))
        if k==1:return None
        if k==2:
            pe=next(e2 for e2 in pairs[p] if e2!=e);row,x=divmod(pe,w+1)
            return ((x-(d==3))%w,(row//2-(d==0))%h)
        dx,dy=task.prior.o1_scan.STEP[d];return ((c[0]+dx)%w,(c[1]+dy)%h)
    def inview(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1]);return max(min(dx,w-dx),min(dy,h-dy))<=3
    def qcontext():
        if uq not in bodies:return None
        qh=bodies[uq][0];occ={c:i for i,b in bodies.items() for c in b};exits=[];blocks=[];enemy=[]
        for d in range(4):
            c=dest(qh,d)
            if c is not None and c not in occ:exits.append(c)
            else:blocks.append(dict(d=d,c=c,owner=occ.get(c),side=teams.get(occ.get(c))))
        for i,b in bodies.items():
            if teams[i]==own:continue
            dirs=[d for d in range(4) if dest(b[0],d)==qh]
            if dirs:enemy.append(dict(i=i,L=len(b),h=b[0],dirs=dirs))
        return dict(r=rnd,q=uq,L=len(bodies[uq]),h=qh,exits=exits,blocks=blocks,enemy_one_step=enemy)
    key=codec.make_key(w,h,codec.team_tag(side));opened={};streams={};cnt=Counter();moments=[];sent_turns=set();hazards=[];qturns=[];qdeaths=[];rnd=-1;actor=None
    for ev in root.pointer(3):
        k,p=ev.u16(0),ev.pointer(0)
        if k==0:rnd=p.i32(0)
        elif k==1:
            actor=p.i32(0)
            if actor==uq:qturns.append(qcontext())
        elif k==9:
            i=p.i32(0);hd,tl=lr.replay.point(p.pointer(0)),lr.replay.point(p.pointer(1));b=bodies[i]
            if b[0]!=hd:b.appendleft(hd)
            while len(b)>1 and b[-1]!=tl:b.pop()
            if i==uq:
                c=qcontext()
                if c['enemy_one_step']:hazards.append(c)
        elif k==10:
            for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
        elif k==11:
            i=p.i32(0)
            if i==uq:qdeaths.append(dict(context=qcontext(),reason=p.u16(4),actor=actor))
            bodies.pop(i)
        elif k==12 and teams.get(p.i32(0))==own:
            wire=p.u64(16)
            if wire not in opened:opened[wire]=codec.unseal(key,wire,streams)
            plain=opened[wire]
            if plain is None:cnt['invalid']+=1;continue
            if (plain >> 63) == 1 and ((plain>>38)&0x7fff)==0x5b and ((plain>>37)&1)==0:
                cell=plain&0x3fff;parts=((plain>>14)&0x3fff)+1;when=(plain>>28)&0x1ff
                cnt['far_rays']+=1
                cnt['far_sender_turns']+= (rnd,p.i32(0)) not in sent_turns
                sent_turns.add((rnd,p.i32(0)))
                m=dict(r=rnd,sender=p.i32(0),cell=cell,parts=parts,when=when,hit=p.i32(12) if p.u16(6) else None)
                if m['hit']==uq and uq in bodies and 0<=rnd-when<=2:
                    cnt['far_hits_queen_fresh']+=1
                    m['queen_head']=bodies[uq][0]
                    m['outside_queen_view']=not inview(bodies[uq][0],(cell%w,cell//w))
                    if m['outside_queen_view']:cnt['far_hits_queen_outside_view']+=1
                moments.append(m)
    cnt['queen_one_step_updates']=len(hazards)
    row=dict(gid=gid,bot=bot,counts=cnt,far_moments=moments,hazards=hazards,queen_turns=qturns,queen_deaths=qdeaths)
    (OUT/f'{gid}-signals.json').write_text(json.dumps(row,ensure_ascii=False))
    rows.append(dict(gid=gid,counts=cnt,far_example=next((m for m in moments if m.get('outside_queen_view')),None),hazard_example=hazards[:1],queen_deaths=qdeaths))
    (OUT/'signals-summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
    print(gid,dict(cnt),flush=True)

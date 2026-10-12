import sys
sys.dont_write_bytecode = True
import importlib.util
import json
from collections import Counter, deque
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[5]
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'data/analysis/ladder/dossier/local')]
import ladder_replay as lr
import scoreboard as sb
spec = importlib.util.spec_from_file_location('shipped_codec', ROOT.parent/'battlecode/work/card_42_check.py')
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)


def scan(gid, folder):
    root = sb.load_replay(folder/f'M{gid}.replay').root()
    meta = json.loads((folder/f'game-{gid}.json').read_text())
    own = int(meta['teamAId'] != 1119)
    w,h = map(int,root.text(0).splitlines()[0].split()[1:3])
    key = codec.make_key(w,h,codec.team_tag('AB'[own]))
    opened,streams = {},{}
    bodies,teams,raw = {},{},[]
    for line in root.text(0).splitlines():
        p=line.split()
        if p[0]=='DRAGON':
            i=len(bodies)
            bodies[i]=deque((int(p[3+2*k]),int(p[4+2*k])) for k in range(int(p[2])))
            teams[i]=int(p[1])
        elif p[0]=='EDGE':raw.append(tuple(map(int,p[1:4])))
    qid=min(i for i in bodies if teams[i]==own)
    eqid=min(i for i in bodies if teams[i]!=own)
    edges=lr.canonical_edges(w,h,raw)
    pairs={}
    for e,(k,p) in edges.items():
        if k==2:pairs.setdefault(p,[]).append(e)
    step=((0,-1),(1,0),(0,1),(-1,0))
    def dest(c,d):
        e=lr.edge_id(w,h,*c,d)
        k,p=edges.get(e,(0,-1))
        if k==1:return None
        if k==2:
            pe=next(z for z in pairs[p] if z!=e)
            row,x=divmod(pe,w+1)
            return ((x-(d==3))%w,(row//2-(d==0))%h)
        return ((c[0]+step[d][0])%w,(c[1]+step[d][1])%h)
    def visible(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1])
        return min(dx,w-dx)<=3 and min(dy,h-dy)<=3
    def context():
        if qid not in bodies:return None
        b=bodies[qid]
        occ={c:i for i,bb in bodies.items() for c in bb}
        return dict(round=rnd,event=index,queen=qid,L=len(b),head=list(b[0]),
                    enemy_queen_alive=eqid in bodies,
                    free=[(d,dest(b[0],d)) for d in range(4) if dest(b[0],d) is not None and dest(b[0],d) not in occ],
                    blocks=[(d,dest(b[0],d),occ.get(dest(b[0],d))) for d in range(4) if dest(b[0],d) is None or dest(b[0],d) in occ],
                    adjacent_enemies=[dict(id=i,L=len(bb),head=list(bb[0]),later=i>qid,
                                           enemy_queen=i==eqid) for i,bb in bodies.items()
                                      if teams[i]!=own and any(dest(bb[0],d)==b[0] for d in range(4))])
    counts=Counter()
    fars,hazards,qt,deaths,stationary=[],[],[],[],[]
    rnd,actor=-1,None
    turn=None
    for index,ev in enumerate(root.pointer(3)):
        k,p=ev.u16(0),ev.pointer(0)
        if k==0:rnd,actor=p.i32(0),None
        elif k==1:
            actor=p.i32(0)
            if actor==qid:qt.append(context())
        elif k==9:
            i=p.i32(0)
            hd,tl=lr.replay.point(p.pointer(0)),lr.replay.point(p.pointer(1))
            b=bodies[i]
            if b[0]!=hd:b.appendleft(hd)
            while len(b)>1 and b[-1]!=tl:b.pop()
            if i==qid:
                c=context()
                if c['adjacent_enemies']:hazards.append(c)
        elif k==10:
            for z,i in enumerate((p.i32(0),p.i32(4))):
                bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z))
                teams[i]=p.u16(8)
            if p.i32(0)==qid:
                c=context()
                if c['adjacent_enemies']:hazards.append(dict(c,split=True))
        elif k==11:
            if p.i32(0)==qid:deaths.append(dict(context=context(),actor=actor,reason=p.u16(4)))
            bodies.pop(p.i32(0))
        elif k==12 and teams.get(p.i32(0))==own:
            wire=p.u64(16)
            if wire not in opened:opened[wire]=codec.unseal(key,wire,streams)
            plain=opened[wire]
            counts['our_sonar']+=1
            if plain is None:
                counts['invalid']+=1
                continue
            if plain>>63 and ((plain>>38)&0x7fff)==0x5b:
                counts['far_sent']+=1
                hit=p.i32(12) if p.u16(6) else None
                cell,parts,when=plain&0x3fff,((plain>>14)&0x3fff)+1,(plain>>28)&0x1ff
                m=dict(round=rnd,event=index,sender=p.i32(0),hit=hit,cell=cell,parts=parts,when=when)
                if hit==qid and qid in bodies and 0<=rnd+1-when<=2:
                    counts['far_received_fresh']+=1
                    m['queen_head']=list(bodies[qid][0])
                    m['outside_view']=not visible(bodies[qid][0],(cell%w,cell//w))
                    counts['far_received_outside_view']+=m['outside_view']
                fars.append(m)
    result=dict(gid=gid,counts=dict(counts),far=fars,queen_turns=qt,
                queen_adjacent_after_move=hazards,queen_deaths=deaths)
    (OUT/f'{gid}-signals.json').write_text(json.dumps(result,separators=(',',':'))+'\n')
    print(gid,dict(counts),'hazards',len(hazards),flush=True)


if __name__=='__main__':
    import importlib.util
    spec=importlib.util.spec_from_file_location('win6task',OUT/'analyze.py')
    task=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(task)
    for gid,label in task.JOBS:
        folder=ROOT/('data/online/smoke/'+label if label else 'data/online/live-one1/b1513119')
        scan(gid,folder)

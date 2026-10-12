"""Mirror-confirmed countdown-1 opportunities; import geometry from existing counter."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import ast, types, json
from collections import defaultdict, deque
sys.path[:0]=['data/analysis/ladder/dossier/online','data/analysis/ladder/dossier/local','data/analysis/ladder/dossier/work']
from label_report import inventory
from spawn import read
from replay_format import point
from analyze import OUT,LABELS
# The old scratch module calls main() unconditionally; omit only that invocation.
p=Path('data/analysis/ladder/dossier/work/sp_tick.py');tree=ast.parse(p.read_text(),filename=str(p))
tree.body=[n for n in tree.body if not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and isinstance(n.value.func,ast.Name) and n.value.func.id=='main')]
mod=types.ModuleType('sp_tick_readonly');exec(compile(tree,str(p),'exec'),mod.__dict__)

def scan(label,path,meta):
    root=read(path);bodies={};teams={};raw=[];sym=''
    for line in root.text(0).splitlines():
        q=line.split()
        if not q:continue
        if q[0]=='MAP':w,h=map(int,q[1:3])
        elif q[0]=='SYMMETRY':sym=q[1]
        elif q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
        elif q[0]=='DRAGON':
            i=len(bodies);teams[i]=int(q[1]);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
    g=mod.Geo(w,h,raw,sym);own=int(meta['teamAId']!=1119);side=lambda i:int(teams[i]!=own)
    rev=[set() for _ in g.nbr]
    for c,ds in enumerate(g.nbr):
        for d in ds:rev[d].add(c)
    def dist(c,srcs):
        seen={c:0};q=deque([c])
        while q:
            x=q.popleft()
            if seen[x]>=3:continue
            for n in rev[x]:
                if n not in seen:seen[n]=seen[x]+1;q.append(n)
        return min((seen.get(x,4) for x in srcs),default=4)
    pos=lambda p:(lambda xy:xy[1]*w+xy[0])(point(p))
    present={};born={};prev=None;steps=set();round_steps=set();lastmeal={};records=[];bad=0;checked=0
    rnd=-1;actor=None;needs=False
    def setup():
        nonlocal prev,steps,round_steps,born,bad,checked
        occ={c for b in bodies.values() for c in b};heads={i:b[0] for i,b in bodies.items()}
        if prev and rnd<=300:
            for c in {g.mirror[x] for x in born if g.mirror[x]!=x}:
                checked+=1
                if c not in born and c not in occ and c not in present:bad+=1;continue
                if c in prev['occ'] or c in prev['pearls']:continue
                for s in (0,1):
                    ids=[i for i,c0 in prev['heads'].items() if side(i)==s and c0 in rev[c]]
                    if not ids:continue
                    entered=any((i,c) in round_steps for i in ids)
                    b=born.get(c)
                    rec=dict(r=rnd,c=c,s=s,ids=ids,entered=entered,born=b is not None,
                             candidate_d=dist(c,[heads[i] for i in ids if i in heads]),
                             team_d=dist(c,[v for i,v in heads.items() if side(i)==s]),
                             recent_meal=any(0<rnd-lastmeal.get((i,c),-999)<=8 for i in ids),eat_s=-1,eat_r=-1,eat_i=-1)
                    records.append(rec)
                    if b is not None:b['watch'].append(rec)
        prev=dict(occ=occ,pearls=set(present),heads=heads)
        born={};round_steps=set()
    for ev in root.pointer(3):
        k=ev.u16(0)
        if k not in (0,1,3,9,10,11):continue
        p=ev.pointer(0)
        if k==0:
            if needs:setup()
            rnd=p.i32(0);actor=None;needs=True
        elif k==1:
            if needs:setup();needs=False
            actor=p.i32(0)
        elif k==3:
            c=pos(p.pointer(0))
            if p.u32(0):
                b=dict(r=rnd,natural=actor is None,watch=[]);present[c]=b
                if b['natural']:born[c]=b
            else:
                b=present.pop(c)
                if b['natural']:lastmeal[actor,c]=rnd
                for rec in b['watch']:rec.update(eat_s=side(actor),eat_r=rnd,eat_i=actor)
        elif k==9:
            i=p.i32(0);hd=pos(p.pointer(0));tl=pos(p.pointer(1));b=bodies[i]
            if b[0]!=hd:b.appendleft(hd);round_steps.add((i,hd))
            while len(b)>1 and b[-1]!=tl:b.pop()
            assert b[-1]==tl
        elif k==10:
            for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(pos(t) for t in p.pointer(z));teams[i]=p.u16(8)
        elif k==11:del bodies[p.i32(0)]
    return dict(label=label,gid=meta['id'],map=meta['mapName'],cells=w*h,w=w,opp=meta['team'+'AB'[1-own]+'Name'],checked=checked,bad=bad,records=records)

if __name__=='__main__':
    for label in sys.argv[1:] or LABELS:
        for path,meta in inventory(label,'old')['jobs']:
            out=OUT/f"clear{meta['id']}.json"
            if out.exists():continue
            result=scan(label,path,meta);out.write_text(json.dumps(result,separators=(',',':')))
            print(label,meta['id'],len(result['records']),'bad',result['bad'],flush=True)

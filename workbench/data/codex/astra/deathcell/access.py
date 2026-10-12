"""Annotate the entrance into an open-edge component, not just the final step before death."""
import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
from collections import deque
import scan

def entrances(g):
    root=scan.lr.agg.sb.load_replay(Path(g['path'])).root();geo=scan.Geo(root.text(0))
    bodies,teams=scan.initial(root.text(0));pearls=set();ways={};recent={};rnd=-1;actor=None;dirs=[];used=0;out={}
    for idx,e in enumerate(root.pointer(3)):
        k=e.u16(0);p=e.pointer(0)
        if k==0:rnd=p.i32(0);actor=None
        elif k==1:actor=p.i32(0);dirs=[];used=0
        elif k==4:
            a=p.pointer(0);dirs=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else [];used=0
        elif k==3:
            c=scan.o1_scan.replay.point(p.pointer(0))
            if p.u32(0):pearls.add(c)
            else:pearls.remove(c)
        elif k==9:
            i=p.i32(0);hd=scan.o1_scan.replay.point(p.pointer(0));tl=scan.o1_scan.replay.point(p.pointer(1));b=bodies[i]
            if b[0]!=hd:
                src=b[0];direction=dirs[used] if i==actor and used<len(dirs) else None
                portal=direction is not None and geo.kind(src,direction)==2
                if portal:recent[i]=dict(r=rnd,src=src,dest=hd)
                if geo.component(src) is not geo.component(hd):
                    ways[i]=dict(r=rnd,portal=portal,src=src,dest=hd,pearls_remaining=len(geo.component(hd)&pearls))
                b.appendleft(hd)
                if i==actor:used+=1
            while len(b)>1 and b[-1]!=tl:b.pop()
        elif k==10:
            parent=p.i32(0);child=p.i32(4);old=bodies[parent][0]
            for z,i in enumerate((parent,child)):
                bb=deque(scan.o1_scan.replay.point(c) for c in p.pointer(z))
                if i==child:
                    if geo.component(old) is geo.component(bb[0]):ways[i]=ways.get(parent);recent[i]=recent.get(parent)
                    else:ways[i]=dict(r=rnd,portal=False,src=None,dest=bb[0],birth=True,pearls_remaining=len(geo.component(bb[0])&pearls))
                bodies[i]=bb;teams[i]=p.u16(8)
        elif k==11:
            i=p.i32(0);out[str(idx)]=dict(component_entrance=ways.get(i),last_portal=recent.get(i));del bodies[i]
    return dict(gid=g['gid'],deaths=out)

if __name__=='__main__':
    games=list(map(json.loads,(scan.OUT/'games.jsonl').read_text().splitlines()))
    with (scan.OUT/'access.jsonl').open('w') as f:
        for n,g in enumerate(games):
            f.write(json.dumps(entrances(g),separators=(',',':'))+'\n');f.flush()
            if n%30==0:print('entrances',n+1,'/',len(games),flush=True)

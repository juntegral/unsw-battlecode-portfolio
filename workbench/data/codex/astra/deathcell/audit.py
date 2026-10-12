"""Replay predicate audit of one proposed immediate self-trap gate, without playing games."""
import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
from collections import defaultdict,Counter,deque
import scan

OUT=scan.OUT

def audit(g):
    root=scan.lr.agg.sb.load_replay(Path(g['path'])).root();geo=scan.Geo(root.text(0))
    bodies,teams=scan.initial(root.text(0));meta=json.loads(Path(g['path']).with_name(f"game-{g['gid']}.json").read_text());own=int(meta['teamAId']!=1119)
    queens={s:min(i for i in bodies if int(teams[i]!=own)==s) for s in (0,1)}
    cap=next((int(l.split()[1]) for l in root.text(0).splitlines() if l.startswith('UNIT_LIMIT ')),64)
    known=defaultdict(set);wins={};rnd=-1;actor=None;pending=None;records=[];dirs=[];used=0
    death_by={d['event']:d for d in g['deaths']};move_by={}
    for idx,e in enumerate(root.pointer(3)):
        k=e.u16(0);p=e.pointer(0)
        if k==0:rnd=p.i32(0);actor=None
        elif k==1:
            actor=p.i32(0);dirs=[];used=0;hd=bodies[actor][0]
            if hd not in wins:
                wins[hd]={scan.edge_id(geo.w,geo.h,*c,d) for c in geo.window(hd) for d in range(4)}
            known[actor]|=wins[hd]
        elif k==4:
            a=p.pointer(0);dirs=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else [];used=0
        elif k==3 and not p.u32(0):pending=scan.o1_scan.replay.point(p.pointer(0))
        elif k==9:
            i=p.i32(0);hd=scan.o1_scan.replay.point(p.pointer(0));tl=scan.o1_scan.replay.point(p.pointer(1));b=bodies[i]
            moved=b[0]!=hd;src=b[0];before=len(b);pearl=pending==hd
            if moved:b.appendleft(hd)
            while len(b)>1 and b[-1]!=tl:b.pop()
            if moved and i==actor:
                direction=dirs[used] if used<len(dirs) else None;used+=1
                # Every exit is observed; unknown portal destinations are an escape, never evidence of a trap.
                all_known=True;self_exit=False
                for z in range(4):
                    edge=scan.edge_id(geo.w,geo.h,*hd,z)
                    if edge not in known[i]:all_known=False;break
                    kind=geo.kind(hd,z)
                    if kind==1:continue
                    if kind==2:
                        pid=geo.edges[edge][1]
                        if not all(a in known[i] for a in geo.portals[pid]):all_known=False;break
                    if geo.dest(hd,z) not in b:self_exit=True
                s=int(teams[i]!=own);queen=i==queens[s]
                split_possible=len(b)>=4 and sum(teams[a]==teams[i] for a in bodies)<cap
                split_safe=False
                if split_possible and not queen:
                    child=list(b)[-2:];remaining=list(b)[:-2]
                    occ={c for a,bb in bodies.items() if a!=i for c in bb}|set(remaining)|set(child)
                    for z in range(4):
                        edge=scan.edge_id(geo.w,geo.h,*child[0],z)
                        if edge not in known[i] or geo.kind(child[0],z)==1:continue
                        if geo.kind(child[0],z)==2 and not all(a in known[i] for a in geo.portals[geo.edges[edge][1]]):continue
                        if geo.dest(child[0],z) not in occ:split_safe=True
                trapped=all_known and not self_exit
                if trapped:
                    rec=dict(event=idx,r=rnd,id=i,side=s,queen=queen,src=src,dest=hd,pearl=pearl,
                             length_before=before,length_after=len(b),portal=direction is not None and geo.kind(src,direction)==2,
                             split_safe=split_safe,reject=queen or not split_safe)
                    records.append(rec);move_by[idx]=rec
            if pearl:pending=None
        elif k==10:
            for z,i in enumerate((p.i32(0),p.i32(4))):
                bodies[i]=deque(scan.o1_scan.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
        elif k==11:del bodies[p.i32(0)]
    links=[]
    for d in g['deaths']:
        ent=d['entry']
        if ent and ent['event'] in move_by:
            a=move_by[ent['event']]
            links.append(dict(event=d['event'],entry_event=ent['event'],side=d['side'],r=d['r'],id=d['id'],
                              queen=d['queen'],cell=d['cell'],length=d['length'],cause=d['cause'],
                              no_enemy3=d['no_enemy3'],reject=a['reject'],split_safe=a['split_safe']))
    return dict(gid=g['gid'],records=records,links=links)

def main():
    games=[json.loads(l) for l in (OUT/'games.jsonl').read_text().splitlines()]
    with (OUT/'audit.jsonl').open('w') as out:
        for n,g in enumerate(games):
            out.write(json.dumps(audit(g),separators=(',',':'))+'\n');out.flush()
            if n%20==0:print('audit',n+1,'/',len(games),flush=True)

if __name__=='__main__':main()

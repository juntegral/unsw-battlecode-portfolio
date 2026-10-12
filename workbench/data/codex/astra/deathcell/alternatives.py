"""Limit the card to a neck-cage entry with another presently legal move."""
import sys
sys.dont_write_bytecode=True
import json
from pathlib import Path
from collections import deque
import scan

if __name__=='__main__':
    gs={g['gid']:g for g in map(json.loads,(scan.OUT/'games.jsonl').read_text().splitlines())}
    audits=list(map(json.loads,(scan.OUT/'audit-narrow.jsonl').read_text().splitlines()))
    for n,a in enumerate(audits):
        targets={r['event']:r for r in a['records'] if r['narrow_reject']}
        if targets:
            g=gs[a['gid']];root=scan.lr.agg.sb.load_replay(Path(g['path'])).root();geo=scan.Geo(root.text(0));bodies,teams=scan.initial(root.text(0));known={};wins={}
            for idx,e in enumerate(root.pointer(3)):
                k=e.u16(0);p=e.pointer(0)
                if k==1:
                    i=p.i32(0);hd=bodies[i][0]
                    if hd not in wins:wins[hd]={scan.edge_id(geo.w,geo.h,*c,z) for c in geo.window(hd) for z in range(4)}
                    known.setdefault(i,set()).update(wins[hd])
                elif k==9:
                    i=p.i32(0);hd=scan.o1_scan.replay.point(p.pointer(0));tl=scan.o1_scan.replay.point(p.pointer(1));b=bodies[i]
                    if idx in targets:
                        src=b[0];occ={c for bb in bodies.values() for c in bb};alternatives=[]
                        for z in range(4):
                            ed=scan.edge_id(geo.w,geo.h,*src,z)
                            if ed not in known[i] or geo.kind(src,z)==1:continue
                            if geo.kind(src,z)==2 and not all(v in known[i] for v in geo.portals[geo.edges[ed][1]]):continue
                            dest=geo.dest(src,z)
                            if dest==hd or dest in occ:continue
                            cage=True
                            for zd in range(4):
                                xd=scan.edge_id(geo.w,geo.h,*dest,zd)
                                if xd not in known[i] or (geo.kind(dest,zd)==2 and not all(v in known[i] for v in geo.portals[geo.edges[xd][1]])):
                                    cage=False;break
                                if geo.kind(dest,zd)!=1 and geo.dest(dest,zd)!=src:cage=False;break
                            if not cage:alternatives.append(dict(dir=z,dest=dest))
                        targets[idx]['alternatives']=alternatives
                        targets[idx]['card_reject']=bool(alternatives)
                    if b[0]!=hd:b.appendleft(hd)
                    while len(b)>1 and b[-1]!=tl:b.pop()
                elif k==10:
                    for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(scan.o1_scan.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
                elif k==11:del bodies[p.i32(0)]
        keep={e for e,r in targets.items() if r['card_reject']}
        for d in a['links']:d['card_reject']=d['entry_event'] in keep
        if n%30==0:print('alternatives',n+1,'/',len(audits),flush=True)
    (scan.OUT/'audit-card.jsonl').write_text(''.join(json.dumps(a,separators=(',',':'))+'\n' for a in audits))

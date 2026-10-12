import sys,json
from pathlib import Path
from collections import deque
sys.dont_write_bytecode=True
sys.path.insert(0,'data/codex/astra/deathcell')
from scan import Geo,initial,lr,o1_scan
OUT=Path(__file__).resolve().parent
for gid,folder in [(1508962,'data/online/live-one1/b1508960'),(1508963,'data/online/live-one1/b1508960'),(1507913,'data/online/smoke/one13-p1-old')]:
    path=Path(folder)/f'M{gid}.replay'
    meta=json.loads(path.with_name(f'game-{gid}.json').read_text())
    root=lr.agg.sb.load_replay(path).root()
    geo=Geo(root.text(0));bodies,teams=initial(root.text(0));own=int(meta['teamAId']!=1119)
    qs=[min(i for i in bodies if (teams[i]==own)==(s==0)) for s in (0,1)]
    rnd=-1;dead=False;found=[];qpath=[];tested=0;cache={}
    def near5(target):
        if target not in cache:
            dist={target:0};queue=deque([target])
            while queue:
                c=queue.popleft()
                if dist[c]==5:continue
                for n in geo.rev[c]:
                    if n not in dist:dist[n]=dist[c]+1;queue.append(n)
            cache[target]=dist
        return cache[target]
    for e in root.pointer(3):
        k,p=e.u16(0),e.pointer(0)
        if k==0:rnd=p.i32(0)
        elif k==1:
            actor=p.i32(0)
            if dead and qs[1] in bodies:
                if actor==qs[1]:qpath.append([rnd,list(bodies[actor][0]),len(bodies[actor])])
                if teams[actor]==own:
                    tested+=1
                    qh=bodies[qs[1]][0];h=bodies[actor][0];dist=near5(qh).get(h,99)
                    if dist<=5:
                        occ={c for i,b in bodies.items() for c in b if c!=qh and c!=h}
                        seen={h:0};qu=deque([h])
                        while qu:
                            c=qu.popleft()
                            if seen[c]==5:continue
                            for d in range(4):
                                n=geo.dest(c,d)
                                if geo.kind(c,d)!=1 and n not in seen and n not in occ:
                                    seen[n]=seen[c]+1;qu.append(n)
                        found.append(dict(r=rnd,id=actor,L=len(bodies[actor]),h=h,qh=qh,terrain=dist,clear=seen.get(qh)))
        elif k==9:
            i=p.i32(0);hd=o1_scan.replay.point(p.pointer(0));tl=o1_scan.replay.point(p.pointer(1));b=bodies[i]
            if hd!=b[0]:b.appendleft(hd)
            while len(b)>1 and b[-1]!=tl:b.pop()
        elif k==10:
            for z,i in enumerate((p.i32(0),p.i32(4))):bodies[i]=deque(o1_scan.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
        elif k==11:
            i=p.i32(0)
            if i==qs[0]:dead=True
            bodies.pop(i)
    result=dict(gid=gid,queens=qs,tested=tested,near=found,enemy_queen_path=qpath)
    (OUT/f'{gid}-proximity.json').write_text(json.dumps(result))
    print(gid,'tested',tested,'near turns',len(found),'clear turns',sum(f['clear'] is not None for f in found),'examples',found[:4], 'queen path endpoints',qpath[:1],qpath[-1:])

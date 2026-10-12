"""Read-only reconstruction; outputs stay beside this script."""
import sys
sys.dont_write_bytecode = True
import importlib.util
import json
import hashlib
from pathlib import Path
from collections import deque

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
sys.path[:0] = [str(ROOT/'tools'), str(ROOT/'data/analysis/ladder/dossier/work')]
import ladder_replay as lr
import o1_scan

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

audit = module('win1_move_audit', ROOT/'data/codex/astra/audit-move/audit.py')
audit.BOTS['21269'] = 'one11'

def details(root, meta):
    geo = audit.Geo(root.text(0))
    bodies, teams = audit.initial(root.text(0))
    own = int(meta['teamAId'] != 1119)
    queens = [min(i for i in bodies if teams[i] == s) for s in (own, 1-own)]
    pearls = set()
    turns, frames, splits, deaths = [], {}, [], []
    rnd, actor, turn = -1, None, None
    def man(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1])
        return min(dx,geo.w-dx)+min(dy,geo.h-dy)
    def free(i):
        occ = {c for b in bodies.values() for c in b}
        return [n for n in geo.moves[bodies[i][0]] if n is not None and n not in occ]
    def snapshot():
        return [dict(alive=sum(teams[i]==s for i in bodies),
                     total=sum(len(b) for i,b in bodies.items() if teams[i]==s),
                     longest=max((len(b) for i,b in bodies.items() if teams[i]==s),default=0),
                     queen=len(bodies.get(q,()))) for s,q in zip((own,1-own),queens)]
    def finish():
        nonlocal turn
        if turn is None:return
        turn['endbody']=list(bodies.get(turn['id'],()))
        turn['queen_end']=list(bodies.get(queens[0],()))
        turn['queen_exits_end']=free(queens[0]) if queens[0] in bodies else []
        turns.append(turn)
        turn=None
    for idx,e in enumerate(root.pointer(3)):
        kind=e.u16(0);p=e.pointer(0)
        if kind==0:
            finish()
            if rnd>=0:frames[rnd]=snapshot()
            rnd,actor=p.i32(0),None
        elif kind==1:
            finish();actor=p.i32(0);body=bodies[actor];head=body[0]
            occ={c:i for i,b in bodies.items() for c in b}
            enemies=[dict(id=i,L=len(b),head=b[0],distance=man(head,b[0]))
                     for i,b in bodies.items() if teams[i]!=teams[actor] and geo.visible(head,b[0])]
            turn=dict(r=rnd,event=idx,id=actor,ours=teams[actor]==own,L=len(body),body=list(body),
                      units=sum(teams[i]==teams[actor] for i in bodies),enemies=enemies,
                      top=min((i for i in bodies if teams[i]==teams[actor]),key=lambda i:(-len(bodies[i]),i)),
                      queen=list(bodies.get(queens[0],())),enemy_queen=list(bodies.get(queens[1],())),
                      free=free(actor),queen_exits=free(queens[0]) if queens[0] in bodies else [],
                      options=[dict(d=d,n=n,owner=occ.get(n),pearl=n in pearls,
                                    edge=geo.edges.get(lr.edge_id(geo.w,geo.h,*head,d),(0,-1)))
                               for d,n in enumerate(geo.moves[head])],ate=[],path=[],dirs=[],split=0)
            if actor in queens:
                turn['state']={i:list(b) for i,b in bodies.items()}
                turn['pearls']=list(pearls)
        elif kind==4:
            a=p.pointer(0)
            turn['action']=a.u16(0) if a else None
            turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) else []
            turn['timeout']=p.bit(32) or bool(p.pointer(1) and p.pointer(1).bit(64))
        elif kind==3:
            c=lr.replay.point(p.pointer(0))
            if p.u32(0):pearls.add(c)
            else:
                pearls.remove(c)
                turn['ate'].append(c)
        elif kind==9:
            i=p.i32(0);h=lr.replay.point(p.pointer(0));tail=lr.replay.point(p.pointer(1));b=bodies[i]
            if h!=b[0]:
                b.appendleft(h)
                if turn and i==actor:turn['path'].append(h)
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
        elif kind==10:
            parent,child=p.i32(0),p.i32(4)
            splits.append(dict(r=rnd,parent=parent,child=child,body=list(bodies[parent]),
                               ours=teams[parent]==own,units=turn['units'],
                               tail_portal=any(geo.edges.get(lr.edge_id(geo.w,geo.h,*bodies[parent][-1],d),(0,-1))[0]==2 for d in range(4))))
            turn['split']=child
            for z,i in enumerate((parent,child)):
                bodies[i]=deque(lr.replay.point(c) for c in p.pointer(z));teams[i]=p.u16(8)
        elif kind==11:
            i=p.i32(0)
            deaths.append(dict(r=rnd,event=idx,id=i,ours=teams[i]==own,L=len(bodies[i]),
                               reason=p.u16(4),actor=actor,free=free(i),head=bodies[i][0]))
            bodies.pop(i)
    finish();frames[rnd]=snapshot()
    result=root.pointer(4)
    for s,z in enumerate((own,1-own)):
        st=result.pointer(z)
        assert tuple(frames[rnd][s][k] for k in ('alive','longest','total','queen'))==tuple(st.i32(k) for k in (0,4,8,12))
    def winning(frame):
        a,b=frame
        if not a['alive'] or not b['alive']:return bool(a['alive']) and not b['alive']
        return tuple(a[k] for k in ('queen','longest','total'))>tuple(b[k] for k in ('queen','longest','total'))
    permanent=max((r for r,f in frames.items() if not winning(f)),default=-1)+1
    return dict(queens=queens,frames=frames,permanent=permanent,turns=turns,splits=splits,deaths=deaths)

def main():
    summaries=[]
    for gid in (1496000,1496002,1496003,1496004):
        path=ROOT/f'data/online/live-one1/b1496000/M{gid}.replay'
        meta=json.loads(path.with_name(f'game-{gid}.json').read_text())
        root=lr.replay.load(path).root()
        assert root.text(2)=='21269' and meta['teamBId']==1119 and meta['teamAId']==62
        assert root.pointer(4).bit(0) and root.pointer(4).u16(6)==1
        base=o1_scan.scan('win1',path,meta)
        ledger=lr.scan(path,meta,'win1',set())
        detail=details(root,meta)
        census=audit.census(path,meta,root)
        output=dict(gid=gid,map=meta['mapName'],bot=21269,
                    replay_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                    base=base,ledger={k:v for k,v in ledger.items() if k not in ('text','intervals')},detail=detail,census=census)
        (OUT/f'g{gid}.json').write_text(json.dumps(output,separators=(',',':'))+'\n')
        summary=dict(gid=gid,map=meta['mapName'],last=base['last'],how=base['how'],
                     final=detail['frames'][base['last']],permanent=detail['permanent'],
                     qdeaths=[d for d in ledger['deaths'] if d['id'] in ledger['queens'].values()],
                     census=census)
        summaries.append(summary)
        print(gid,summary['how'],summary['permanent'],summary['final'],flush=True)
    (OUT/'summary.json').write_text(json.dumps(summaries,indent=2)+'\n')

if __name__=='__main__':main()

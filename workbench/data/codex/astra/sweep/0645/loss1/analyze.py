import sys, json
from pathlib import Path
from collections import deque, Counter
sys.dont_write_bytecode = True
sys.path[:0] = ['data/analysis/ladder/dossier/local', 'tools']
import scoreboard
from count_local import Geo
from ladder_replay import edge_id, canonical_edges

OUT = Path(__file__).parent
def scan(gid):
    root = scoreboard.load_replay(Path(f'data/online/smoke/one11-p1-old/M{gid}.replay')).root()
    w,h = map(int,root.text(0).splitlines()[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in root.text(0).splitlines():
        q=line.split()
        if q[0]=='DRAGON':
            i=len(bodies); teams[i]=int(q[1]); bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
        elif q[0]=='EDGE': raw.append(tuple(map(int,q[1:4])))
    geo=Geo(w,h,raw); edges=canonical_edges(w,h,raw)
    queens=[min(i for i in bodies if teams[i]==s) for s in (0,1)]
    rnd=-1; actor=None; turn=None; pearls={}; turns=[]; deaths=[]; snapshots={}; qboards=[]
    distance_cache={}; approaches=[]; all_min=None; near_events=0; selected=[]
    def xy(c): return [c%w,c//w]
    def ball(target):
        if target not in distance_cache:
            # Reverse graph accounts for directed portal entries.
            d={target:0}; queue=deque([target])
            while queue:
                c=queue.popleft()
                for z in reverse[c]:
                    if z not in d: d[z]=d[c]+1; queue.append(z)
            distance_cache[target]=d
        return distance_cache[target]
    reverse=[[] for _ in geo.adj]
    for a,ns in enumerate(geo.adj):
        for b in ns: reverse[b].append(a)
    def state():
        return [dict(alive=sum(teams[i]==s for i in bodies),total=sum(len(b) for i,b in bodies.items() if teams[i]==s),queen=len(bodies.get(queens[s],[])),longest=sorted([[len(b),i,xy(b[0])] for i,b in bodies.items() if teams[i]==s],reverse=True)[:5]) for s in (0,1)]
    def board(who=None):
        who=queens[0] if who is None else who
        hd=bodies[who][0]; occ={c:('Q' if i==who and j==0 else 'q' if i==who else 'A' if teams[i]==0 and j==0 else 'a' if teams[i]==0 else 'E' if j==0 else 'e') for i,b in bodies.items() for j,c in enumerate(b)}
        rows=[]; erows=[]
        for dy in range(-3,4):
            chars=[]; es=[]
            for dx in range(-3,4):
                c=((hd//w+dy)%h)*w+(hd%w+dx)%w
                chars.append(occ.get(c,'*' if c in pearls else '.'))
                mask=sum(1<<d for d,(k,t) in enumerate(geo.moves[c]) if k==1)
                es.append(format(mask,'x'))
            rows.append(''.join(chars)); erows.append(''.join(es))
        return dict(round=rnd,id=who,head=xy(hd),body=[xy(c) for c in bodies[who]],cells=rows,kelp=erows,near=[dict(id=i,side=teams[i],length=len(b),body=[xy(c) for c in b]) for i,b in bodies.items() if any(c in geo.window(hd) for c in b)])
    def close():
        if turn is not None:
            turn['end']=xy(bodies[turn['id']][0]) if turn['id'] in bodies else None
            turn['Lend']=len(bodies.get(turn['id'],[])); turns.append(turn)
    for ix,ev in enumerate(root.pointer(3)):
        k=ev.u16(0); p=ev.pointer(0)
        if k==0:
            close(); turn=None
            if rnd>=0: snapshots[rnd]=state()
            rnd=p.i32(0); actor=None
        elif k==1:
            close(); actor=p.i32(0)
            turn=dict(round=rnd,event=ix,id=actor,side=teams[actor],units=sum(teams[i]==teams[actor] for i in bodies),length=len(bodies[actor]),head=xy(bodies[actor][0]),path=[],eat=0,natural=0,action=None)
            if actor==queens[0]: qboards.append(board())
            if teams[actor]==0 and len(bodies[actor])>=10: selected.append(board(actor))
            if queens[0] not in bodies and queens[1] in bodies and teams[actor]==0:
                target=bodies[queens[1]][0]; dist=ball(target).get(bodies[actor][0],99)
                if dist<=5: approaches.append(dict(round=rnd,id=actor,length=len(bodies[actor]),distance=dist,head=xy(bodies[actor][0]),queen=xy(target)))
        elif k==3:
            c=scoreboard.replay_format.point(p.pointer(0)); c=c[1]*w+c[0]
            if p.u32(0): pearls[c]=actor is None
            else:
                natural=pearls.pop(c); turn['eat']+=1; turn['natural']+=natural
        elif k==4:
            a=p.pointer(0)
            if a: turn['action']={'kind':a.u16(0),'dirs':list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) is not None else [],'arg':a.i32(4)}
        elif k==9:
            i=p.i32(0); hd=scoreboard.replay_format.point(p.pointer(0)); tl=scoreboard.replay_format.point(p.pointer(1)); hd=hd[1]*w+hd[0]; tl=tl[1]*w+tl[0]
            b=bodies[i]
            if hd!=b[0]: b.appendleft(hd); turn['path'].append(xy(hd))
            while len(b)>1 and b[-1]!=tl: b.pop()
            assert b[-1]==tl
        elif k==10:
            for z,i in enumerate((p.i32(0),p.i32(4))):
                bodies[i]=deque(pt.i32(4)*w+pt.i32(0) for pt in p.pointer(z)); teams[i]=p.u16(8)
            turn['split']=[p.i32(0),p.i32(4)]
        elif k==11:
            i=p.i32(0)
            deaths.append(dict(round=rnd,event=ix,id=i,side=teams[i],length=len(bodies[i]),head=xy(bodies[i][0]),reason=p.u16(4),actor=actor,actor_start=turn.copy() if turn else None))
            bodies.pop(i)
        if k in (1,9,10,11) and queens[0] not in bodies and queens[1] in bodies:
            target=bodies[queens[1]][0]; d=ball(target)
            nearest=min([(d.get(b[0],9999),i) for i,b in bodies.items() if teams[i]==0],default=(9999,-1))
            near_events+=nearest[0]<=5
            if all_min is None or nearest[0]<all_min['distance']:
                all_min=dict(round=rnd,event=ix,distance=nearest[0],id=nearest[1],queen=xy(target),head=xy(bodies[nearest[1]][0]) if nearest[1]>=0 else None)
    close(); snapshots[rnd]=state()
    final=root.pointer(4)
    for s in (0,1):
        r=final.pointer(s); st=snapshots[rnd][s]
        assert [st['alive'],st['longest'][0][0] if st['longest'] else 0,st['total'],st['queen']]==[r.i32(o) for o in (0,4,8,12)]
    return dict(gid=gid,bot=[root.text(1),root.text(2)],size=[w,h],queens=queens,final=snapshots[rnd],snapshots=snapshots,deaths=deaths,turns=turns,qboards=qboards,selected=selected,approaches=approaches,all_min=all_min,near_events=near_events)

if __name__=='__main__':
    for gid in [1498737,1498738,1498739]:
        data=scan(gid); (OUT/f'{gid}-detail.json').write_text(json.dumps(data))
        print(gid,'QDEATH',[d for d in data['deaths'] if d['id'] in data['queens']], 'APPROACHES',len(data['approaches']),data['approaches'][:3],flush=True)

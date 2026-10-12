import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import deque, Counter

ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tools'))
import ladder_replay as lr
sys.path.insert(0, str(ROOT / 'data/analysis/ladder/dossier/local'))
import scoreboard as sb
counter = sb.load_counter()

def run(gid):
    path = ROOT / f'data/online/smoke/one13-c2-old/M{gid}.replay'
    root = sb.load_replay(path).root()
    meta = json.loads(path.with_name(f'game-{gid}.json').read_text())
    lr.replay.load = lambda _: type('Loaded', (), {'root': lambda _: root})()
    base = lr.scan(path, meta, path.parent.name, set())
    base.pop('intervals')
    (OUT / f'{gid}-scan.json').write_text(json.dumps(base))
    w,h = map(int, root.text(0).splitlines()[0].split()[1:3])
    bodies, teams, edges = {}, {}, []
    for line in root.text(0).splitlines():
        p = line.split()
        if p and p[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(p[4+2*k])*w+int(p[3+2*k]) for k in range(int(p[2])))
            teams[i] = int(p[1])
        elif p and p[0] == 'EDGE':
            edges.append(tuple(map(int,p[1:4])))
    geo = counter.Geo(w,h,edges)
    q = base['queens']['us']; eq = base['queens']['them']
    qdeath = next(d for d in base['deaths'] if d['id'] == q)
    deathround = qdeath['round']
    turns, snaps, boards, selected = [], {}, [], []
    pearls=set(); origins={}; rnd=-1; actor=None; turn=None
    coords=lambda c: [c%w,c//w]
    tile=lambda p: p.i32(4)*w+p.i32(0)
    minimum=99999; close=None; close_turns=[]; qplaces=set(); qpositions=[]
    occup=lambda: {c:(i,k) for i,b in bodies.items() for k,c in enumerate(b)}
    def snapshot():
        return {str(i): {'side':teams[i], 'length':len(b), 'head':coords(b[0])} for i,b in bodies.items()}
    def picture(center):
        cx,cy=coords(center); occ=occup(); rows=[]
        for dy in range(-3,4):
            top=''; mid=''
            for dx in range(-3,4):
                x,y=(cx+dx)%w,(cy+dy)%h;c=y*w+x
                north=geo.moves[c][0][0];west=geo.moves[c][3][0]
                top+='+'+('#' if north==1 else '@' if north==2 else '-')
                ch='*' if c in pearls else '.'
                if c in occ:
                    i,k=occ[c]
                    ch=('Q' if i==q else 'K' if i==eq else 'A' if teams[i]==0 else 'B') if k==0 else ('q' if i==q else 'k' if i==eq else 'a' if teams[i]==0 else 'b')
                mid+=('#' if west==1 else '@' if west==2 else '|')+ch
            rows.append(top+'+')
            c=((cy+dy)%h)*w+(cx+3)%w
            rows.append(mid+('#' if geo.moves[c][1][0]==1 else '@' if geo.moves[c][1][0]==2 else '|'))
        bottom=''
        for dx in range(-3,4):
            c=((cy+3)%h)*w+(cx+dx)%w
            bottom+='+'+('#' if geo.moves[c][2][0]==1 else '@' if geo.moves[c][2][0]==2 else '-')
        rows.append(bottom+'+')
        nearby={str(i):{'side':teams[i],'body':[coords(c) for c in b]} for i,b in bodies.items() if any(min(abs(c%w-cx),w-abs(c%w-cx))<=3 and min(abs(c//w-cy),h-abs(c//w-cy))<=3 for c in b)}
        return {'round':rnd,'center':coords(center),'rows':rows,'nearby':nearby}
    def proximity(event, own_turn=False):
        nonlocal minimum,close
        if q in bodies or eq not in bodies:return
        hd=bodies[eq][0];qplaces.add(hd)
        dist=geo.distances(hd)
        cand=[(dist[b[0]],i,b[0]) for i,b in bodies.items() if teams[i]==0]
        if not cand:return
        d,i,c=min(cand)
        if d<minimum:
            minimum=d;close={'round':rnd,'event':event,'distance':d,'id':i,'head':coords(c),'queen':coords(hd)}
        if own_turn and actor in bodies and teams[actor]==0 and dist[bodies[actor][0]]<=5:
            close_turns.append({'round':rnd,'id':actor,'length':len(bodies[actor]),'head':coords(bodies[actor][0]),'queen':coords(hd),'distance':dist[bodies[actor][0]]})
    def endturn():
        if turn is not None:
            turn['end']=coords(bodies[actor][0]) if actor in bodies else None
            turn['end_length']=len(bodies.get(actor,()))
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:
            endturn()
            if rnd>=0:snaps[rnd]=snapshot()
            rnd=p.i32(0);actor=None;turn=None
        elif k==1:
            endturn();actor=p.i32(0)
            turn={'round':rnd,'id':actor,'side':teams[actor],'length':len(bodies[actor]),'head':coords(bodies[actor][0]),'moves':[],'eat':0,'drop_eat':0,'split':None,'action':None}
            turns.append(turn)
            if actor==q and rnd>=deathround-3:
                pic=picture(bodies[q][0]);pic['turn']=turn;boards.append(pic)
            if deathround-4<=rnd<=deathround+1:
                selected.append({'event':idx, 'round':rnd, 'actor':actor, 'bodies':{str(i):[coords(c) for c in b] for i,b in bodies.items()}})
            proximity(idx,True)
        elif k==3:
            c=tile(p.pointer(0))
            if p.u32(0):pearls.add(c);origins[c]=actor is not None
            else:
                pearls.remove(c);turn['eat']+=1;turn['drop_eat']+=origins.pop(c)
        elif k==4:
            a=p.pointer(0)
            turn['action']={'kind':a.u16(0),'dirs':list(a.pointer(0)) if a.u16(0)==0 and a.pointer(0) else []}
        elif k==9:
            i=p.i32(0);hd=tile(p.pointer(0));tail=tile(p.pointer(1));b=bodies[i]
            if b[0]!=hd:b.appendleft(hd);turn['moves'].append(coords(hd))
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
            proximity(idx)
        elif k==10:
            par,ch=p.i32(0),p.i32(4)
            turn['split']=ch
            for z,i in enumerate((par,ch)):
                bodies[i]=deque(tile(c) for c in p.pointer(z));teams[i]=p.u16(8)
            proximity(idx)
        elif k==11:
            i=p.i32(0)
            if i==q:
                pic=picture(bodies[q][0]);pic['actor']=actor;pic['event']=idx;boards.append(pic)
            bodies.pop(i)
            proximity(idx)
    endturn();snaps[rnd]=snapshot()
    for side in (0,1):
        st=root.pointer(4).pointer(side);ls=[len(b) for i,b in bodies.items() if teams[i]==side]
        assert [len(ls),max(ls),sum(ls)]==[st.i32(0),st.i32(4),st.i32(8)]
    def rank(st):
        a=[d['length'] for d in st.values() if d['side']==0];b=[d['length'] for d in st.values() if d['side']==1]
        qa=st.get(str(q),{}).get('length',0);qb=st.get(str(eq),{}).get('length',0)
        aa=(qa,max(a,default=0),sum(a));bb=(qb,max(b,default=0),sum(b))
        return -1 if aa<bb else 1 if aa>bb else 0
    permanent=max((r for r,st in snaps.items() if rank(st)>=0),default=-1)+1
    data={'gid':gid,'size':[w,h],'queens':[q,eq],'final':snaps[rnd],'permanent_behind':permanent,'boards':boards,'nearest_after_queen_death':close,'close_turns':close_turns,'enemy_queen_cells_after_death':[coords(c) for c in sorted(qplaces)],'turns':turns,'snapshots':snaps,'selected':selected}
    (OUT/f'{gid}-detail.json').write_text(json.dumps(data))
    print(gid,'permanent',permanent,'near',close,'close turns',len(close_turns),flush=True)
    for pic in boards:
        print('BOARD',pic['round'],pic['center'],pic.get('turn'),flush=True)
        print('\n'.join(pic['rows']),flush=True)
        print('NEARBY',pic['nearby'],flush=True)

if __name__=='__main__':
    for gid in map(int,sys.argv[1:] or [1510784,1510785,1510786]):run(gid)

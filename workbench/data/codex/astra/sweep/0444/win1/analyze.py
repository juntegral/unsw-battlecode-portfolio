import sys
sys.dont_write_bytecode = True
import json
from pathlib import Path
from collections import deque, Counter
sys.path.insert(0, 'tools')
import ladder_replay as lr
sys.path.insert(0, 'data/analysis/ladder/dossier/local')
from count_local import Geo

OUT = Path(__file__).resolve().parent

def analyze(folder, gid):
    path = Path('data/online/live-one1') / folder / f'M{gid}.replay'
    meta = json.loads(path.with_name(f'game-{gid}.json').read_text())
    base = lr.scan(path, meta, folder, set())
    base.pop('intervals')
    root = lr.replay.load(path).root()
    W, H = map(int, root.text(0).splitlines()[0].split()[1:3])
    bodies, teams, raw = {}, {}, []
    for line in root.text(0).splitlines():
        q = line.split()
        if q and q[0] == 'DRAGON':
            i = len(bodies)
            bodies[i] = deque(int(q[4+2*k])*W+int(q[3+2*k]) for k in range(int(q[2])))
            teams[i] = int(q[1])
        elif q and q[0] == 'EDGE':
            raw.append(tuple(map(int,q[1:4])))
    geo = Geo(W,H,raw)
    qu, qt = base['queens']['us'], base['queens']['them']
    tile = lambda p: lr.replay.point(p)[1]*W+lr.replay.point(p)[0]
    xy = lambda c: [c%W,c//W]
    def man(a,b):
        dx,dy=abs(a%W-b%W),abs(a//W-b//W)
        return min(dx,W-dx)+min(dy,H-dy)
    def state():
        return {str(i): dict(side=teams[i], length=len(b), body=[xy(c) for c in b]) for i,b in bodies.items()}
    def exits(i):
        occupied=set(c for b in bodies.values() for c in b)
        return [xy(t) for k,t in geo.moves[bodies[i][0]] if k!=1 and t not in occupied]
    rnd,actor,turn=-1,None,None
    present=set(); turns=[]; moments=[]; snaps={}; logs=Counter()
    def close():
        if turn is None: return
        turn['end'] = xy(bodies[actor][0]) if actor in bodies else None
        turn['Lend'] = len(bodies.get(actor,()))
        turns.append(turn)
    for idx,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:
            close();turn=None
            if rnd>=0:snaps[rnd]=state()
            rnd,actor=p.i32(0),None
        elif k==1:
            close();actor=p.i32(0)
            h=bodies[actor][0];occ={c for b in bodies.values() for c in b}
            adj=[t for wall,t in geo.moves[h] if wall!=1 and t in present and t not in occ]
            mates=[b[0] for i,b in bodies.items() if teams[i]==teams[actor] and i!=actor]
            nearest=min(mates,key=lambda c:man(h,c),default=None)
            turn=dict(r=rnd,i=actor,side=teams[actor],L=len(bodies[actor]),start=xy(h),
                      dirs=[],steps=[],eaten=[],deaths=[],split=False,adjpearls=[xy(c) for c in adj],
                      nearestmate=xy(nearest) if nearest is not None else None,
                      queen=xy(bodies[qu][0]) if qu in bodies else None,
                      enemyqueen=xy(bodies[qt][0]) if qt in bodies else None,
                      enemyqueenL=len(bodies.get(qt,())),
                      enemies=[dict(i=i,L=len(b),h=xy(b[0]),dist=man(h,b[0])) for i,b in bodies.items() if teams[i]!=teams[actor] and man(h,b[0])<=5],
                      count=sum(teams[i]==teams[actor] for i in bodies),exits=exits(actor))
            if actor==qu and ((gid==1488845 and 30<=rnd<=36) or (gid==1488843 and 91<=rnd<=97)):
                moments.append(dict(r=rnd,event=idx,kind='queen_turn',state=state(),exits=exits(qu)))
        elif k==4:
            a=p.pointer(0)
            turn['action']=a.u16(0) if a else None
            if a and a.u16(0)==0 and a.pointer(0):turn['dirs']=list(a.pointer(0))
        elif k==3:
            c=tile(p.pointer(0))
            if p.u32(0):present.add(c)
            else:
                present.remove(c)
                turn['eaten'].append(xy(c))
        elif k==9:
            i=p.i32(0);h,t=tile(p.pointer(0)),tile(p.pointer(1));b=bodies[i]
            if b[0]!=h:
                b.appendleft(h)
                if turn is not None:turn['steps'].append(xy(h))
            while len(b)>1 and b[-1]!=t:b.pop()
            assert b[-1]==t
        elif k==10:
            turn['split']=True
            for z,i in enumerate((p.i32(0),p.i32(4))):
                bodies[i]=deque(tile(pt) for pt in p.pointer(z));teams[i]=p.u16(8)
            if qu in bodies and man(bodies[qu][0],bodies[p.i32(4)][0])<=2:
                moments.append(dict(r=rnd,event=idx,kind='split_near_queen',parent=p.i32(0),child=p.i32(4),state=state(),exits=exits(qu)))
        elif k==11:
            i=p.i32(0)
            turn['deaths'].append(dict(i=i,reason=p.u16(4),L=len(bodies[i])))
            if i in (qu,qt):moments.append(dict(r=rnd,event=idx,kind='queen_death',id=i,state=state()))
            bodies.pop(i)
        elif k in (5,6,7):logs[str(k)]+=1
    close();snaps[rnd]=state()
    for side, key in ((0,'us'),(1,'them')):
        lengths=[len(b) for i,b in bodies.items() if teams[i]==side]
        final=base['final'][key]
        assert (len(lengths),sum(lengths),max(lengths,default=0)) == (final['alive'],final['total'],final['longest'])
    def score(s,side):
        arr=[(i,d) for i,d in s.items() if d['side']==side]
        return (int(bool(arr)),s.get(str(qu if side==0 else qt),{}).get('length',0),max((d['length'] for i,d in arr),default=0),sum(d['length'] for i,d in arr))
    trailing=[r for r,s in snaps.items() if score(s,0)<=score(s,1)]
    ahead=max(trailing)+1 if trailing else 0
    assert all(score(s,0)>score(s,1) for r,s in snaps.items() if r>=ahead)
    own=[t for t in turns if t['side']==0]
    patterns={
      'adjacent_pearl_turns':sum(bool(t['adjpearls']) for t in own),
      'adjacent_pearl_no_eat':sum(bool(t['adjpearls']) and not t['eaten'] for t in own),
      'late_stop':sum(t.get('action')==2 and t['r']>400 for t in own),
      'own_initiated_queen_rams':sum(any(d['i']==qt and d['reason']==3 for d in t['deaths']) for t in own),
      'herd_nearer_turns':sum(t['i']==qu and t['nearestmate'] is not None and t['end'] is not None and man(t['end'][1]*W+t['end'][0],t['nearestmate'][1]*W+t['nearestmate'][0])<man(t['start'][1]*W+t['start'][0],t['nearestmate'][1]*W+t['nearestmate'][0]) for t in own),
    }
    result=dict(gid=gid,base=base,turns=turns,moments=moments,snaps=snaps,ahead_forever=ahead,patterns=patterns,logs=dict(logs),W=W,H=H)
    (OUT/f'{gid}.json').write_text(json.dumps(result,ensure_ascii=False))
    print(gid,'ahead',ahead,'patterns',patterns)
    print('queen last turns',[t for t in own if t['i']==qu][-7:])
    print('ram',[t for t in own if any(d['i']==qt for d in t['deaths'])])
    print('late stop examples',[t for t in own if t.get('action')==2 and t['r']>400][:3])
    print('herd examples',[t for t in own if t['i']==qu and t['nearestmate'] and t['end'] and man(t['end'][1]*W+t['end'][0],t['nearestmate'][1]*W+t['nearestmate'][0])<man(t['start'][1]*W+t['start'][0],t['nearestmate'][1]*W+t['nearestmate'][0])][:3])

if __name__=='__main__':
    analyze('b1488845',1488845)
    analyze('b1488840',1488843)

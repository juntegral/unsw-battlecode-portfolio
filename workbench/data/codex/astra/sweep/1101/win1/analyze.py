import sys
sys.dont_write_bytecode = True
import json
import hashlib
from pathlib import Path
from collections import Counter, defaultdict, deque

ROOT = Path.cwd()
OUT = ROOT / 'data/codex/astra/sweep/1101/win1'
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'data/analysis/ladder/dossier/work'))
import ladder_replay as lr
import o1_scan

IDS = (1518019, 1518020, 1518022, 1518023)
MASK = (1 << 64) - 1
CHECK = 255 << 55
CIPHER = MASK ^ (CHECK | (3 << 53))

def rot(x, b):
    return ((x << b) | (x >> (64-b))) & MASK

def prf(key, m):
    v = [key[0] ^ 0x736f6d6570736575, key[1] ^ 0x646f72616e646f6d,
         key[0] ^ 0x6c7967656e657261, key[1] ^ 0x7465646279746573]
    def rounds(n):
        for _ in range(n):
            v[0] = (v[0]+v[1]) & MASK
            v[1] = rot(v[1],13) ^ v[0]
            v[0] = rot(v[0],32)
            v[2] = (v[2]+v[3]) & MASK
            v[3] = rot(v[3],16) ^ v[2]
            v[0] = (v[0]+v[3]) & MASK
            v[3] = rot(v[3],21) ^ v[0]
            v[2] = (v[2]+v[1]) & MASK
            v[1] = rot(v[1],17) ^ v[2]
            v[2] = rot(v[2],32)
    v[3] ^= m
    rounds(2)
    v[0] ^= m
    v[3] ^= 8 << 56
    rounds(2)
    v[0] ^= 8 << 56
    v[2] ^= 255
    rounds(4)
    return v[0] ^ v[1] ^ v[2] ^ v[3]

assert prf((0x0706050403020100,0x0f0e0d0c0b0a0908),0x0706050403020100) == 0x93f5f5799a932462

def analyze(gid):
    path = ROOT / f'data/online/live-one1/b1518019/M{gid}.replay'
    meta = json.loads(path.with_name(f'game-{gid}.json').read_text())
    base = lr.scan(path, meta, str(path.parent), set())
    econ = o1_scan.scan('win1',path,meta)
    assert base['bots']['A'] == '21497' and base['winner'] == 'A'
    root = lr.replay.load(path).root()
    lines = root.text(0).splitlines()
    w,h = map(int,lines[0].split()[1:3])
    bodies,teams,raw = {},{},[]
    for line in lines:
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies)
            bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])))
            teams[i]='AB'[int(q[1])]
        elif q and q[0]=='EDGE':
            raw.append(tuple(map(int,q[1:4])))
    edges=lr.canonical_edges(w,h,raw)
    portals=defaultdict(list)
    for e,(kind,pid) in edges.items():
        if kind==2:portals[pid].append(e)
    def dest(pos,d):
        e=lr.edge_id(w,h,*pos,d)
        kind,pid=edges.get(e,(0,-1))
        if kind==1:return None
        if kind==2:
            partner=next(z for z in portals[pid] if z!=e)
            row,x=divmod(partner,w+1)
            return ((x-(d==3))%w,(row//2-(d==0))%h)
        dx,dy=((0,-1),(1,0),(0,1),(-1,0))[d]
        return ((pos[0]+dx)%w,(pos[1]+dy)%h)
    def gap(a,b):
        return min(abs(a[0]-b[0]),w-abs(a[0]-b[0]))+min(abs(a[1]-b[1]),h-abs(a[1]-b[1]))
    def in_view(a,b):
        return min(abs(a[0]-b[0]),w-abs(a[0]-b[0]))<=3 and min(abs(a[1]-b[1]),h-abs(a[1]-b[1]))<=3
    def free(pos):
        occupied=set(c for b in bodies.values() for c in b)
        return [z for d in range(4) if (z:=dest(pos,d)) is not None and z not in occupied]
    qid=base['queens']['us']
    secret=0xe1de70530c48de42
    rootkey=(secret,rot(secret,29)^0xa5a5a5a5a5a5a5a5)
    game=(w<<40)|(h<<16)|2
    key=(prf(rootkey,game),prf(rootkey,game|(1<<63)))
    pads={b:prf(key,CHECK|b)&CIPHER for b in range(256)}
    decode_cache={}
    def decode(wire):
        if wire not in decode_cache:
            check=(wire>>55)&255
            plain=(wire & (MASK^CHECK)) ^ pads[check]
            decode_cache[wire]=plain if (prf(key,plain & (MASK^CHECK))&255)==check else None
        return decode_cache[wire]
    rounds={}
    turns=[]
    queen_turns=[]
    near_events=[]
    far=[]
    event_types=Counter()
    rnd=-1
    queen_last_turn=-1
    actor=None
    turn=None
    present=set()
    seen=defaultdict(set)
    last_facing={}
    def state():
        out={}
        for team in 'AB':
            ls=[len(b) for i,b in bodies.items() if teams[i]==team]
            qi=base['queens']['us' if team=='A' else 'them']
            out[team]=[len(ls),max(ls,default=0),sum(ls),len(bodies.get(qi,()))]
        return out
    initial=state()
    def finish():
        if turn is None:return
        i=turn['id']
        turn['after']=list(bodies[i][0]) if i in bodies else None
        turn['Lafter']=len(bodies.get(i,()))
        turn['used']=used
        turn['dead']=i not in bodies
        turn['ate']=ate
        if teams[i]=='A':
            turns.append(turn)
            if i==qid:queen_turns.append(turn)
    for idx,ev in enumerate(root.pointer(3)):
        kind=lr.replay.EVENT_NAMES[ev.u16(0)]
        event_types[kind]+=1
        p=ev.pointer(0)
        if kind=='roundStart':
            finish()
            if rnd>=0:rounds[rnd]=state()
            rnd=p.i32(0)
            actor=None
            turn=None
        elif kind=='turnStart':
            finish()
            actor=p.i32(0)
            if actor==qid:queen_last_turn=rnd
            bb=bodies[actor]
            hd=bb[0]
            used=ate=0
            dirs=[]
            freecells=free(hd)
            turn=dict(r=rnd,id=actor,L=len(bb),head=list(hd),units=state()['A'][0],
                      free=len(freecells),pearls=[list(c) for c in freecells if c in present],
                      eaten=[],
                      queen=actor==qid,steps=[],action=None,split=None,
                      foes=[dict(id=i,L=len(b),head=list(b[0]),gap=gap(hd,b[0]),visible=in_view(hd,b[0]))
                            for i,b in bodies.items() if teams[i]!=teams[actor] and gap(hd,b[0])<=8],
                      previous_facing=last_facing.get(actor))
            for y in range(-3,4):
                for x in range(-3,4):seen[actor].add(((hd[0]+x)%w,(hd[1]+y)%h))
        elif kind=='dragonAction':
            a=p.pointer(0)
            turn['action']=a.u16(0) if a else None
            dirs=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
            turn['steps']=dirs
            cursor=tuple(turn['head'])
            turn['portals']=[]
            for step,d in enumerate(dirs):
                z=dest(cursor,d)
                if z is None:break
                e=lr.edge_id(w,h,*cursor,d)
                if edges.get(e,(0,-1))[0]==2:
                    turn['portals'].append(dict(step=step,exit=list(z),unseen=z not in seen[actor]))
                cursor=z
        elif kind=='tileChange':
            c=lr.replay.point(p.pointer(0))
            if p.u32(0):present.add(c)
            else:
                present.remove(c)
                ate+=1
                turn['eaten'].append(list(c))
        elif kind=='dragonUpdate':
            i=p.i32(0)
            hd=lr.replay.point(p.pointer(0))
            tail=lr.replay.point(p.pointer(1))
            b=bodies[i]
            if b[0]!=hd:
                b.appendleft(hd)
                if i==actor:
                    if used<len(dirs):last_facing[i]=dirs[used]
                    used+=1
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
        elif kind=='dragonSplit':
            parent,child=p.i32(0),p.i32(4)
            for k,i in enumerate((parent,child)):
                bodies[i]=deque(lr.replay.point(c) for c in p.pointer(k))
                teams[i]='AB'[p.u16(8)]
            turn['split']=[len(bodies[parent]),len(bodies[child])]
        elif kind=='dragonDeath':
            i=p.i32(0)
            if i==qid or (qid in bodies and teams[i]=='B' and p.u16(4)==3 and gap(bodies[i][0],bodies[qid][0])<=3):
                near_events.append(dict(r=rnd,id=i,actor=actor,reason=p.u16(4),
                                        length=len(bodies[i]),head=list(bodies[i][0]),
                                        actor_turn=dict(turn),state=state()))
            bodies.pop(i)
        elif kind=='sonarPing' and teams.get(p.i32(0))=='A':
            plain=decode(p.u64(16))
            if plain is not None and (plain>>63) and ((plain>>38)&0x7fff)==0x5b:
                cell=plain & 0x3fff
                endpoint=lr.replay.point(p.pointer(1))
                recipients=[i for i,b in bodies.items() if endpoint in b]
                far.append(dict(r=rnd,sender=p.i32(0),head=[cell%w,cell//w],parts=((plain>>14)&0x3fff)+1,
                                when=(plain>>28)&511,hitKind=p.u16(24),pointers=[lr.replay.point(p.pointer(k)) for k in range(p.pwords)],
                                recipients=recipients,queen_last_turn=queen_last_turn,event=idx,
                                databytes=p._bytes(0,p.dwords*8).hex()))
    finish()
    rounds[rnd]=state()
    assert rounds[rnd]['A'][:3]==[base['final']['us'][k] for k in ('alive','longest','total')]
    assert rounds[rnd]['B'][:3]==[base['final']['them'][k] for k in ('alive','longest','total')]
    def cmp(s):
        a,b=s['A'],s['B']
        if not a[0] or not b[0]:return (a[0]>0)-(b[0]>0)
        return ((a[3],a[1],a[2])>(b[3],b[1],b[2]))-((a[3],a[1],a[2])<(b[3],b[1],b[2]))
    leads={r:cmp(s) for r,s in rounds.items()}
    decisive=next(r for r in rounds if all(leads[k]>0 for k in rounds if k>=r))
    last_nonlead=max((r for r,v in leads.items() if v<=0),default=None)
    qdeaths=[d for d in base['deaths'] if d['id'] in base['queens'].values()]
    return dict(gid=gid,map=meta['mapName'],sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                queens=base['queens'],initial=initial,final=base['final'],last=base['last_round'],how=econ['how'],
                decisive=decisive,last_nonlead=last_nonlead,lead_ranges={str(v):[r for r,z in leads.items() if z==v] for v in (-1,0,1)},
                states=rounds,qdeaths=qdeaths,queen_turns=queen_turns,near_events=near_events,turns=turns,
                far=far,event_types=event_types,econ=econ,anomalies=base['anomalies'],
                drop_recovery=Counter(p['eater'] for p in base['pearls'] if p['drop_side']=='us'),
                own_no_action=[d for d in base['deaths'] if d['side']=='us' and d['reason']==4])

if __name__=='__main__':
    rows=[]
    for gid in IDS:
        x=analyze(gid)
        (OUT/f'{gid}.json').write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
        rows.append(x)
        print(gid,x['how'],'lead',x['decisive'],'qdeaths',[(d['id'],d['round'],d['length']) for d in x['qdeaths']],flush=True)
    (OUT/'summary.json').write_text(json.dumps({
        'games':[dict(gid=x['gid'],map=x['map'],final=x['final'],decisive=x['decisive'],last=x['last'],how=x['how'],
                      far=len(x['far']),event_types=x['event_types'],own_no_action=len(x['own_no_action']),drop_recovery=x['drop_recovery']) for x in rows],
        'definition':'Rounds are replay zero-based, states are end of round; ahead compares elimination, queen, longest, total.'
    },ensure_ascii=False,indent=2)+'\n')

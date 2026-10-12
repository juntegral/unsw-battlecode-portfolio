import sys
sys.dont_write_bytecode = True
import gzip, json, subprocess
from pathlib import Path
from collections import Counter, deque, defaultdict
from functools import lru_cache

ROOT = Path.cwd()
OUT = ROOT / 'data/codex/astra/sweep/1055/win8'
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'data/analysis/ladder/dossier/local'))
import ladder_replay as lr
import replay_format as rf

IDS1 = [1509103,1509104,1509105,1509106,1509110]
IDS2 = [1513833,1513835,1513837,1513838,1513841,1513843]
JOBS = [ROOT/f'data/online/smoke/one13-k1-old/M{i}.replay' for i in IDS1]
JOBS += [ROOT/f'data/online/smoke/one13-k2-old/M{i}.replay' for i in IDS2]
JOBS += [ROOT/'data/online/live-one1/b1508580/M1508580.replay']

def read(path):
    blob = path.read_bytes()
    if blob[:2] == b'\x1f\x8b': blob = gzip.decompress(blob)
    return rf.Message(subprocess.run([str(ROOT/'data/analysis/ladder/dossier/target/tg_unpack')], input=blob, stdout=subprocess.PIPE, check=True).stdout)

MASK=(1<<64)-1;CHECK=255<<55;TAG=3<<53
def rot(x,b): return ((x<<b)|(x>>(64-b)))&MASK
def prf(key,m):
    a,b,c,d=key[0]^0x736f6d6570736575,key[1]^0x646f72616e646f6d,key[0]^0x6c7967656e657261,key[1]^0x7465646279746573
    def rounds(a,b,c,d,n):
        for _ in range(n):
            a=(a+b)&MASK;b=rot(b,13)^a;a=rot(a,32)
            c=(c+d)&MASK;d=rot(d,16)^c
            a=(a+d)&MASK;d=rot(d,21)^a
            c=(c+b)&MASK;b=rot(b,17)^c;c=rot(c,32)
        return a,b,c,d
    d^=m;a,b,c,d=rounds(a,b,c,d,2);a^=m;d^=8<<56
    a,b,c,d=rounds(a,b,c,d,2);a^=8<<56;c^=255
    a,b,c,d=rounds(a,b,c,d,4)
    return a^b^c^d
assert prf((0x0706050403020100,0x0f0e0d0c0b0a0908),0x0706050403020100)==0x93f5f5799a932462
def make_key(w,h,tag):
    secret=0xe1de70530c48de42;root=(secret,rot(secret,29)^0xa5a5a5a5a5a5a5a5);m=(w<<40)|(h<<16)|tag
    return prf(root,m),prf(root,m|(1<<63))
@lru_cache(maxsize=200000)
def decode(key,wire):
    check=(wire>>55)&255;stream=prf(key,CHECK|check)&(MASK^CHECK^TAG);plain=(wire&(MASK^CHECK))^stream
    return plain if prf(key,plain&(MASK^CHECK))&255==check else None

def extra(root,base):
    lines=root.text(0).splitlines();w,h=map(int,lines[0].split()[1:3]);bodies={};teams={};raw=[]
    for line in lines:
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies);teams[i]=int(q[1]);bodies[i]=deque(int(q[4+2*k])*w+int(q[3+2*k]) for k in range(int(q[2])))
        elif q and q[0]=='EDGE':raw.append(tuple(map(int,q[1:4])))
    own='AB'.index(base['ours']);queen=base['queens']['us'];foe=base['queens']['them']
    edges=lr.canonical_edges(w,h,raw);portals=defaultdict(list)
    for e,(k,p) in edges.items():
        if k==2:portals[p].append(e)
    moves=[]
    for y in range(h):
        for x in range(w):
            row=[]
            for d,(dx,dy) in enumerate(lr.base.STEP):
                e=lr.edge_id(w,h,x,y,d);k,p=edges.get(e,(0,-1))
                if k==2:
                    partner=next(z for z in portals[p] if z!=e);ry,px=divmod(partner,w+1);dest=((ry//2-(d==0))%h)*w+(px-(d==3))%w
                else:dest=((y+dy)%h)*w+(x+dx)%w
                row.append((k,dest))
            moves.append(row)
    @lru_cache(maxsize=None)
    def dist3(src):
        found={src:0};q=deque([src])
        while q:
            c=q.popleft()
            if found[c]>=3:continue
            for k,n in moves[c]:
                if k!=1 and n not in found:found[n]=found[c]+1;q.append(n)
        return found
    def view(src):return {((src//w+dy)%h)*w+(src%w+dx)%w for dy in range(-3,4) for dx in range(-3,4)}
    def record(name,t,**kw):
        counts[name]+=1
        if len(examples[name])<3:examples[name].append(dict(round=t['r'],id=t['i'],length=t['L'],head=t['head'],**kw))
    seen=defaultdict(set);present=set();counts=Counter();examples=defaultdict(list);qturns=[];turn=None;rnd=-1
    turns=[];sonar=Counter();sonarex=[];keys={s:make_key(w,h,2 if s==0 else 1) for s in (0,1)}
    def close():
        nonlocal turn
        if turn is None:return
        t=turn;i=t['i']
        if teams[i]==own:
            if not t['split'] and t['steps']==0:
                record('no_step_no_split',t,action=t['action'],died=t['died'])
                if t['action']==2:record('suicide',t)
            if t['pearls']:record('eating_turn',t,pearls=t['pearls'])
            if t['available'] and not t['pearls'] and not t['split'] and t['steps'] and not t['died']:
                record('adjacent_empty_entry_pearl_pass',t,available=t['available'],end=t['end'])
                if t['clean_available']:record('adjacent_no_enemy3_pearl_pass',t,available=t['clean_available'],end=t['end'])
            if t['L']>=8 and i!=queen and t['steps']>=2 and t['enemy3'] and not t['died'] and not t['portal']:
                record('long_multistep_threat_escape_proxy',t,steps=t['steps'],end=t['end'])
            if i==queen:
                qturns.append(t)
                if t['L']<=3:record('queen_short',t)
                if t['adjacent_enemy']:record('queen_adjacent_enemy',t,enemies=t['adjacent_enemy'])
                if len(t['empty_exits'])<=1:record('queen_at_most_one_empty_exit',t,exits=t['empty_exits'])
                if t['available'] and t['pearls']:record('queen_adjacent_eat',t)
            if t['split'] and i==queen:record('queen_split',t,end_length=t['endL'])
            if t['queen_kill']:record('active_enemy_queen_ram',t,steps=t['steps']+1,target_length=t['queen_kill'])
            if t['defend_ram']:record('active_ram_enemy_near_queen',t,targets=t['defend_ram'])
            turns.append({k:t[k] for k in ('r','i','L','head','steps','split','action','died','pearls','end','endL','enemy3','queen_kill')})
        turn=None
    for evindex,ev in enumerate(root.pointer(3)):
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:close();rnd=p.i32(0)
        elif k==1:
            close();i=p.i32(0);b=bodies[i];hd=b[0];occ={c for bb in bodies.values() for c in bb};seen[i].update(view(hd))
            enemies={z:bb[0] for z,bb in bodies.items() if teams[z]!=own};near=[z for z,c in enemies.items() if dist3(hd).get(c,99)<=3]
            avail=[n for kk,n in moves[hd] if kk!=1 and n in present and n not in occ]
            clean=[n for n in avail if not any(dist3(n).get(c,99)<=3 for c in enemies.values())]
            turn=dict(r=rnd,i=i,L=len(b),head=hd,end=hd,endL=len(b),steps=0,pearls=0,split=False,action=None,died=False,
                      enemy3=near,available=avail,clean_available=clean,portal=False,queen_kill=0,defend_ram=[],
                      adjacent_enemy=[z for z,c in enemies.items() if any(kk!=1 and n==c for kk,n in moves[hd])],
                      empty_exits=[n for kk,n in moves[hd] if kk!=1 and n not in occ],
                      queen_length=len(bodies.get(queen,())),foe_queen_length=len(bodies.get(foe,())),
                      own_count=sum(teams[z]==own for z in bodies),enemy_count=sum(teams[z]!=own for z in bodies))
        elif k==3:
            xy=rf.point(p.pointer(0));c=xy[1]*w+xy[0]
            if p.u32(0):present.add(c)
            else:present.remove(c);turn['pearls']+=1
        elif k==4:
            a=p.pointer(0);turn['action']=a.u16(0) if a else None
            turn['dirs']=list(a.pointer(0)) if a and a.u16(0)==0 and a.pointer(0) is not None else []
        elif k==9:
            i=p.i32(0);xy=rf.point(p.pointer(0));tl=rf.point(p.pointer(1));hd=xy[1]*w+xy[0];tail=tl[1]*w+tl[0];b=bodies[i]
            if b[0]!=hd:
                if turn and i==turn['i']:
                    ds=turn.get('dirs',[]);used=turn['steps']
                    if used<len(ds) and moves[b[0]][ds[used]][0]==2:turn['portal']=True
                    turn['steps']+=1;turn['end']=hd
                b.appendleft(hd)
            while len(b)>1 and b[-1]!=tail:b.pop()
            assert b[-1]==tail
            if turn and i==turn['i']:turn['endL']=len(b)
        elif k==10:
            for z,i in enumerate((p.i32(0),p.i32(4))):
                bodies[i]=deque(pt.i32(4)*w+pt.i32(0) for pt in p.pointer(z));teams[i]=p.u16(8)
            turn['split']=True;turn['endL']=len(bodies[turn['i']])
        elif k==11:
            i=p.i32(0);reason=p.u16(4)
            if turn and i==turn['i']:turn['died']=True;turn['endL']=0
            if reason==3 and turn and i!=turn['i'] and teams[turn['i']]==own and teams[i]!=own:
                if i==foe:turn['queen_kill']=len(bodies[i])
                elif queen in bodies and dist3(bodies[queen][0]).get(bodies[i][0],99)<=3:turn['defend_ram'].append(i)
            bodies.pop(i)
        elif k==12:
            wire=p.u64(16);tag=(wire>>53)&3;s=0 if tag==2 else 1 if tag==1 else -1
            if s==own:
                plain=decode(keys[s],wire)
                if plain is not None and plain>>63 and ((plain>>38)&0x7fff)==0x5b:
                    sonar['far_head_ping_events']+=1
                    if len(sonarex)<5:sonarex.append(dict(round=rnd,event=evindex,data=[p.u64(i*8) for i in range(p.dwords)],cell=plain&0x3fff,length=((plain>>14)&0x3fff)+1,sighting_round=(plain>>28)&0x1ff))
    close()
    return dict(counts=dict(counts),examples=dict(examples),queen_turns=qturns,turns=turns,sonar=dict(sonar),sonar_examples=sonarex)

def main():
    allrows=[]
    for path in JOBS:
        gid=int(path.stem[1:]);j=json.loads(path.with_name(f'game-{gid}.json').read_text());msg=read(path);root=msg.root();lr.replay.load=lambda _:msg
        base=lr.scan(path,j,path.parent.name,set())
        assert base['bots'][base['ours']]=='21377',(gid,base['bots'])
        assert base['winner']==base['ours'],(gid,base['winner'])
        def score(s):return (int(s['alive']>0),s['queen_length'],s['longest'],s['total'])
        rounds=sorted(base['snapshots']);last_not_ahead=max((r for r in rounds if score(base['snapshots'][r]['us'])<=score(base['snapshots'][r]['them'])),default=-1)
        base['ahead_for_good']=next((r for r in rounds if r>last_not_ahead),None)
        final=base['final'];base['decision']='extinction' if not final['them']['alive'] else next(key for key in ('queen_length','longest','total') if final['us'][key]!=final['them'][key])
        ex=extra(root,base);row=dict(base=base,extra=ex)
        (OUT/f'{gid}.json').write_text(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n');allrows.append(row)
        print(gid,j['mapName'],base['decision'],final,'ahead',base['ahead_for_good'],flush=True)
    totals=Counter();sonar=Counter();examples=defaultdict(list)
    for row in allrows:
        totals.update(row['extra']['counts']);sonar.update(row['extra']['sonar'])
        for name,ee in row['extra']['examples'].items():
            for e in ee:examples[name].append(dict(game=row['base']['gid'],**e))
    (OUT/'aggregate.json').write_text(json.dumps(dict(counts=totals,sonar=sonar,examples=examples),ensure_ascii=False,indent=2)+'\n')
    print('totals',totals,'sonar',sonar,flush=True)

if __name__=='__main__':main()

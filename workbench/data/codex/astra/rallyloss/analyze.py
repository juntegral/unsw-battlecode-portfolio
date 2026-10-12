import sys
sys.dont_write_bytecode = True
import json, csv, hashlib
from pathlib import Path
from collections import Counter, defaultdict, deque
from datetime import datetime
sys.path[:0] = ['tools', 'data/analysis/ladder/dossier/work', 'data/analysis/ladder/dossier/online', 'data/codex/astra/longest']
import o1_scan, label_report
from ladder_replay import replay
import analyze as previous

OUT = Path('data/codex/astra/rallyloss')
MASK = (1 << 64) - 1
CHECK = 255 << 55
TAG = 3 << 53
def rot(x,n): return ((x << n) | (x >> (64-n))) & MASK
def prf(key,m):
    v = [key[0]^0x736f6d6570736575,key[1]^0x646f72616e646f6d,key[0]^0x6c7967656e657261,key[1]^0x7465646279746573]
    def rounds(n):
        for _ in range(n):
            v[0]=(v[0]+v[1])&MASK; v[1]=rot(v[1],13)^v[0];v[0]=rot(v[0],32)
            v[2]=(v[2]+v[3])&MASK; v[3]=rot(v[3],16)^v[2]
            v[0]=(v[0]+v[3])&MASK; v[3]=rot(v[3],21)^v[0]
            v[2]=(v[2]+v[1])&MASK; v[1]=rot(v[1],17)^v[2];v[2]=rot(v[2],32)
    v[3]^=m;rounds(2);v[0]^=m;v[3]^=8<<56;rounds(2);v[0]^=8<<56;v[2]^=255;rounds(4)
    return v[0]^v[1]^v[2]^v[3]
assert prf((0x0706050403020100,0x0f0e0d0c0b0a0908),0x0706050403020100)==0x93f5f5799a932462
def wire_decoder(W,H,tag):
    root=(0xe1de70530c48de42,rot(0xe1de70530c48de42,29)^0xa5a5a5a5a5a5a5a5)
    game=(W<<40)|(H<<16)|tag;key=(prf(root,game),prf(root,game|(1<<63)))
    pads={c:prf(key,CHECK|c)&(MASK^(CHECK|TAG)) for c in range(256)}
    memo={}
    def decode(w):
        if w not in memo:
            c=(w>>55)&255;p=(w&(MASK^CHECK))^pads[c]
            memo[w]=p if prf(key,p&(MASK^CHECK))&255==c else None
        return memo[w]
    return decode

def trace(path,j,b,g):
    root=replay.load(path).root();lines=root.text(0).splitlines();W,H=map(int,lines[0].split()[1:3]);own=int(j['teamAId']!=1119)
    bodies={};teams={};tokens={};labels=defaultdict(set);serial=0
    def new():
        nonlocal serial
        serial+=1;return serial
    for line in lines:
        q=line.split()
        if q and q[0]=='DRAGON':
            i=len(bodies);bodies[i]=deque((int(q[3+2*k]),int(q[4+2*k])) for k in range(int(q[2])));teams[i]=int(int(q[1])!=own);tokens[i]=deque(new() for _ in bodies[i])
    queens=g['queens']; decode=wire_decoder(W,H,2 if own==0 else 1)
    def gap(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1]);return min(dx,W-dx)+min(dy,H-dy)
    def top(s):return max((i for i in bodies if teams[i]==s),key=lambda i:(len(bodies[i]),-i),default=None)
    events=list(root.pointer(3));wires=defaultdict(list);logs=defaultdict(list);r=-1;a=None
    for ev in events:
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:r=p.i32(0);a=None
        elif k==1:a=p.i32(0)
        elif k==12 and a is not None and teams.get(a,own)==0:
            plain=decode(p.u64(16))
            if plain is not None and plain>>63==0:
                wires[r,a].append(dict(id=(plain&65535)&32767,queen_game=bool(plain&32768),length=(plain>>16)&4095,round=(plain>>28)&511,pos=((plain>>37)&127,(plain>>44)&127)))
        elif k==6:logs[r,a].append(p.text(0))
    records={};seen=set();current=None;present={};pending=None;deathsrc=None;expected=0;deathn=0;arrivals=[];fed=set();dissipated=Counter();received=defaultdict(set);received_target=defaultdict(set);end_hold=defaultdict(set);direct=[];fed_deaths=[];coverage=Counter();queen_games=set();eaten_by=defaultdict(set);ever_final=defaultdict(set);lastwire={};transported=defaultdict(set)
    def candidate(i,leader,kind):
        key=f'{kind}:{i}'
        if key in seen:return
        seen.add(key)
        rec=dict(id=i,side=teams[i],kind=kind,round=r,length=len(bodies[i]),leader=leader['id'],leader_length=leader['length'],leader_when=leader['round'],head=list(bodies[i][0]),target=list(leader['pos']),distance=gap(bodies[i][0],leader['pos']),arrival=None,advertised_arrival=None,death=None,move_rounds=0,inward_rounds=0,first_generation=[],ever_top=[],ever_target=[],end_top=[],lost_tokens=0,remaining_tokens=0)
        records[key]=rec
        for t in tokens[i]:labels[t].add(key)
    def arrive():
        tops={s:top(s) for s in (0,1)}
        for key,c in records.items():
            i=c['id'];lead=tops[c['side']]
            if c['arrival'] is None and i in bodies and lead is not None and i!=lead and gap(bodies[i][0],bodies[lead][0])<=3:
                c['arrival']=[r,lead,gap(bodies[i][0],bodies[lead][0])]
    def close_turn():
        if current is None:return
        i=current['id'];lead=current['wire']; moved=current.get('moved',False)
        if lead and i in bodies and lead['id'] in bodies and gap(bodies[i][0],bodies[lead['id']][0])<=3:
            for key in (f'rally-proxy:{i}',f'cohort400:{i}'):
                if key in records and records[key]['advertised_arrival'] is None:records[key]['advertised_arrival']=[r,lead['id'],gap(bodies[i][0],bodies[lead['id']][0])]
        if current['eligible'] and moved and i in bodies:
            coverage['eligible_moving_turns']+=1
            if gap(bodies[i][0],lead['pos'])<current['distance']:
                coverage['eligible_inward_turns']+=1
                key=f'rally-proxy:{i}'
            key=f'rally-proxy:{i}'
            if key in records:
                records[key]['move_rounds']+=1
                records[key]['inward_rounds']+=gap(bodies[i][0],lead['pos'])<current['distance']
        arrive()
    r=-1;a=None
    for ev in events:
        k=ev.u16(0);p=ev.pointer(0)
        if k==0:
            close_turn();current=None;r=p.i32(0);a=None
            if r==401:
                for s in (0,1):
                    lead=top(s)
                    if lead is not None:
                        for i in list(bodies):
                            if teams[i]==s and i!=queens[s] and i!=lead and len(bodies[i])*2<=len(bodies[lead]):candidate(i,dict(id=lead,length=len(bodies[lead]),round=r,pos=bodies[lead][0]),'cohort400')
        elif k==1:
            close_turn();a=p.i32(0);lead=(wires.get((r,a)) or [None])[0];eligible=False
            if lead:lastwire[a]=lead
            if lead and lead['queen_game']:queen_games.add(a)
            if teams[a]==0 and r>(300 if a in queen_games else 400):
                coverage['post400_our_turns']+=1;coverage['leader_wire_turns']+=lead is not None
                eligible=lead is not None and a!=queens[0] and a!=lead['id'] and r-lead['round']<=25 and len(bodies[a])*2<=lead['length'] and gap(bodies[a][0],lead['pos'])>15 and sum(teams[i]==0 for i in bodies)>3
                if eligible:candidate(a,lead,'rally-proxy')
            current=dict(id=a,head=bodies[a][0],L=len(bodies[a]),wire=lead,eligible=eligible,distance=gap(bodies[a][0],lead['pos']) if lead else None,before_tokens=list(tokens[a]))
            arrive()
        elif k==3:
            cell=replay.point(p.pointer(0))
            if p.u32(0):
                if expected:
                    dt,seg=deathsrc['drop_tokens'].popleft();assert cell==seg
                    present[cell]=(dt,deathsrc);expected-=1
                else:present[cell]=(new(),None)
            else:
                pending=present.pop(cell);t,src=pending
                if src is not None:eaten_by[a].add(t)
                if src is not None:
                    lead=top(teams[a]);row=dict(round=r,eater=a,side=teams[a],top=lead==a,target_top=lead,source=src['id'],source_side=src['side'],death_round=src['round'],cause=src['cause'],cell=list(cell),wait=r-src['round'])
                    direct.append(row);src['eaters'].append(row)
                    if teams[a]==src['side'] and src['cause']=='stop':fed.add(a)
                    for key in labels[t]:
                        if records[key]['side']==teams[a]:transported[key].add(t)
                        if records[key]['side']==teams[a] and a==lead:received[key].add(t)
                        if a==records[key]['leader']:received_target[key].add(t)
                        if src['id']==records[key]['id']:records[key]['first_generation'].append(row)
        elif k==4 and current is not None:
            action=p.pointer(0);usage=p.pointer(1)
            current['action_kind']=action.u16(0) if action else None
            current['timeout']=p.bit(32) or bool(usage and usage.bit(64))
        elif k==9:
            i=p.i32(0);h,tail=replay.point(p.pointer(0)),replay.point(p.pointer(1));bb=bodies[i];tt=tokens[i]
            if bb[0]!=h:
                newtoken=pending[0] if pending is not None else tt.pop()
                if pending is not None:pending=None
                bb.appendleft(h);tt.appendleft(newtoken)
                removed=0
                while len(bb)>1 and bb[-1]!=tail:bb.pop();removed+=1
                if newtoken is not None and len(tt)>len(bb):
                    while len(tt)>len(bb):
                        gone=tt.pop()
                        for key in labels[gone]:dissipated[key]+=1
                assert len(tt)==len(bb)
                if current and i==a:current['moved']=True
            assert bb[-1]==tail
        elif k==10:
            i,child=p.i32(0),p.i32(4);bycell=dict(zip(bodies[i],tokens[i]));teams[child]=teams[i]
            for z,unit in enumerate((i,child)):
                bodies[unit]=deque(replay.point(c) for c in p.pointer(z));tokens[unit]=deque(bycell[c] for c in bodies[unit])
        elif k==11:
            i=p.i32(0);old=b['deaths'][deathn];deathn+=1;bb=bodies[i];tt=tokens[i];lead=top(teams[i]);near=gap(bb[0],bodies[lead][0]) if lead is not None and lead!=i else 0
            d=dict(id=i,side=teams[i],round=r,length=len(bb),cause=old[4],head=list(bb[0]),top_id=lead,top_length=len(bodies[lead]) if lead is not None else 0,distance=near,extra=old[18],free=old[5],fed=i in fed,eaters=[],actor=a,action_kind=current.get('action_kind') if current else None,timeout=current.get('timeout') if current else None,reason=p.u16(4))
            exact_wire=(wires.get((r,i)) or [None])[0];wire=exact_wire or lastwire.get(i)
            d['wire_on_death_turn']=exact_wire is not None
            d['advertised_leader']=wire
            d['advertised_distance']=gap(bb[0],bodies[wire['id']][0]) if wire and wire['id'] in bodies else None
            if r>=350 and i in fed:fed_deaths.append(d)
            for key,c in records.items():
                if c['id']==i and c['death'] is None:c['death']=d
            if teams[i]==1 and r>=350 and i!=queens[1] and lead!=i and len(bb)*2<=len(bodies[lead]) and old[4] in ('stop','own body') and near<=3:
                candidate(i,dict(id=lead,length=len(bodies[lead]),round=r,pos=bodies[lead][0]),'fold');records[f'fold:{i}']['death']=d;records[f'fold:{i}']['arrival']=[r,lead,near]
            for z,t in enumerate(tt):
                if z%2:
                    for key in labels[t]:dissipated[key]+=1
            d['drop_tokens']=deque((t,c) for z,(t,c) in enumerate(zip(tt,bb)) if z%2==0);deathsrc=d;expected=len(d['drop_tokens']);bodies.pop(i);tokens.pop(i)
    close_turn();assert pending is None and expected==0
    for s in (0,1):
        lead=top(s)
        if lead is not None:
            for t in eaten_by[lead]:
                for key in labels[t]:
                    if records[key]['side']==s:ever_final[key].add(t)
            for t in tokens[lead]:
                for key in labels[t]:end_hold[key].add(t)
    alive_tokens={t for tt in tokens.values() for t in tt}|{t for t,src in present.values()}
    for key,c in records.items():
        c['ever_top']=len(received[key]);c['ever_target']=len(received_target[key]);c['end_top']=len(end_hold[key]);c['lost_tokens']=dissipated[key];c['remaining_tokens']=sum(key in labels[t] for t in alive_tokens)
        c['ever_final_top']=len(ever_final[key]);c['end_final_transferred']=len(end_hold[key]&ever_final[key])
        c['end_transported']=len(end_hold[key]&transported[key]);c['transported']=len(transported[key])
        assert c['lost_tokens']+c['remaining_tokens']==c['length'],(j['id'],key,c)
        if c['death']:c['death'].pop('drop_tokens',None)
    for d in fed_deaths:d.pop('drop_tokens',None)
    return dict(schema=4,records=list(records.values()),direct=direct,fed_deaths=fed_deaths,coverage=dict(coverage),token_residuals=0)

def main():
    sets=['one6-w1','one5-w1','one6-c1','one5-c1'];inventory=[]
    cache={}
    if (OUT/'base.jsonl').exists():cache={x['gid']:x for x in map(json.loads,(OUT/'base.jsonl').read_text().splitlines())}
    done={}
    if (OUT/'games.jsonl').exists():done={x['gid']:x for x in map(json.loads,(OUT/'games.jsonl').read_text().splitlines())}
    with (OUT/'base.jsonl').open('a') as bf,(OUT/'games.jsonl').open('w') as gf:
        for label in sets:
            inv=label_report.inventory(label,'old');inventory.append(dict(label=label,available=len(inv['jobs']),planned=inv['planned'],notes=inv['notes']))
            for path,j in inv['jobs']:
                b=cache.get(j['id'])
                if b is None:b=o1_scan.scan(label,path,j);bf.write(json.dumps(b,separators=(',',':'))+'\n');bf.flush()
                g=done.get(j['id'])
                if b['last']<200:
                    root=replay.load(path).root();own=int(j['teamAId']!=1119);initial=[int(line.split()[1]) for line in root.text(0).splitlines() if line.startswith('DRAGON ')]
                    queens=[next(i for i,t in enumerate(initial) if int(t!=own)==s) for s in (0,1)]
                    snap=[dict(id=None,length=x[2],alive=x[0],total=x[1]) for x in b['ends']]
                    if g is None:g=dict(gid=j['id'],label=label,map=b['map'],opp=b['opp'],last=b['last'],queens=queens,result=b['result'],snapshots={str(b['last']):snap},all_dragons={})
                    else:g['queens']=queens
                if g is None:g=previous.detail(path,j,b)
                g['base']=b
                if g.get('trace',{}).get('schema')!=4:g['trace']=trace(path,j,b,g)
                gf.write(json.dumps(g,separators=(',',':'))+'\n');gf.flush();print(label,j['id'],b['map'],b['last'],len(g['trace']['records']),flush=True)
    (OUT/'inventory.json').write_text(json.dumps(dict(time=datetime.now().astimezone().isoformat(),sets=inventory),indent=2,ensure_ascii=False))
if __name__=='__main__':main()

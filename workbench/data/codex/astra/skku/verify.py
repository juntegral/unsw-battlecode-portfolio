import sys
sys.dont_write_bytecode=True
sys.path[:0]=['tools','data/codex/astra/stuck-opus']
import json,hashlib
from pathlib import Path
from collections import Counter
from ladder_replay import edge_id,canonical_edges
from geom import geometry
P=Path('data/codex/astra/skku');games=[json.loads(p.read_text()) for p in sorted(P.glob('15*.json'))]
assert len(games)==10
checked=0;out=[];bybattle={};deaths=[];attacks=[[],[]]
for g in games:
    s=g['scan'];b=g['base'];d=g['detail'];gid=s['gid'];j=g['meta']
    expected='21377' if gid<1519937 else '21497'
    assert b['bots'][b['ours']]==s['bot']==expected
    assert b['winner']==j['winner'].upper()
    assert (b['winner']==b['ours'])==(s['result']=='win')
    for r,ss in s['snaps'].items():
        for sd,key in enumerate(('us','them')):
            v=b['snapshots'][r][key]
            assert ss[sd][:4]==[v['alive'],v['total'],v['longest'],v['queen_length']]
            checked+=1
    bybattle.setdefault(b['folder'],Counter())[s['result']]+=1
    G=geometry(b['text']);W,H=d['W'],d['H'];raw=[tuple(map(int,z.split()[1:4])) for z in b['text'].splitlines() if z.startswith('EDGE ')]
    edges=canonical_edges(W,H,raw)
    for de in d['deaths']:
        if de['id'] not in d['queens']:continue
        if de['reason']==3 and de['actor']!=de['id'] and de['attack']['s']!=de['s']:
            a=de['attack'];attacks[a['s']].append(dict(gid=gid,r=de['r'],id=a['id'],L=a['L'],steps=a['steps'],free=a['free'],paid=a['paid'],distance=a['distance']))
        if de['s']==0 and s['result']=='loss':
            assert de['reason']==3 and de['actor']!=de['id']
            assert de['attack']['seen_last'] and not any(de['attack']['portal'])
            deaths.append(de)
            last=de['last'][-1];h=last['h'];occ={tuple(c) for bb in last['bodies'].values() for c in bb};exits=[]
            for k,(dx,dy) in enumerate(((0,-1),(1,0),(0,1),(-1,0))):
                if edges.get(edge_id(W,H,*h,k),(0,-1))[0]!=0:continue
                c=((h[0]+dx)%W,(h[1]+dy)%H)
                if c not in occ:exits.append(('NESW'[k],c))
            out.append(dict(gid=gid,queen=de['id'],r=de['r'],L=de['L'],ordinary_exits=exits,attacker=de['actor'],spent=de['attack']['spent_before_collision']))
audit=dict(games=len(games),snapshot_side_checks=checked,battles=bybattle,loss_queen_deaths=len(deaths),already_dead=sum(not x['enemy_queen_alive'] for x in deaths),attack_steps=Counter(x['attack']['steps'] for x in deaths),last_exits=out,queen_attacks=attacks)
paths=['data/online/smoke/one14-bot/main.cpp','data/online/smoke/one13-bot/main.cpp',str(Path.home()/'meow-redteam/solo/bots/mBoth/main.cpp'),str(Path.home()/'meow-redteam/solo/src/w-one16/main.cpp')]
assert Path(paths[1]).read_text().replace('constexpr int PORTAL_SCOUT_MIN_LEN = 4;','constexpr int PORTAL_SCOUT_MIN_LEN = 0;')==Path(paths[0]).read_text()
audit['one13_to_one14_only_portal_scout_change']=True
audit['sources']={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}
(P/'verification.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))

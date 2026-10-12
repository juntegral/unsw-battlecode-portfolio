import sys
sys.dont_write_bytecode = True
import importlib.util, json
from pathlib import Path
from collections import Counter, defaultdict
sys.path.insert(0, 'tools')
import ladder_replay as lr
OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('existing_sonar_codec', '../battlecode/work/card_42_check.py')
codec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(codec)
rows = json.loads((OUT/'measurements.json').read_text())
audit = json.loads((OUT/'switch-audit.json').read_text())
totals = Counter(); moments = defaultdict(list); games = defaultdict(set); details = []
def add(key,g,t):
    totals[key] += 1; games[key].add(g['gid'])
    if len(moments[key]) < 3:
        moments[key].append(dict(game=g['gid'],round=t['round'],dragon=t.get('id'),head=t.get('head')))
for g in rows:
    gid=g['gid']; folder = 'data/online/smoke/one12-k1-old' if gid in (1504483,1504485,1504487,1504488,1504490,1504491) else 'data/online/live-one1/'+('b1504730' if gid in (1504730,1504732,1504733,1504734) else 'b1501263')
    path=Path(folder)/f'M{gid}.replay'; meta=json.loads(path.with_name(f'game-{gid}.json').read_text())
    base=json.loads((OUT/f'{gid}-base.json').read_text())
    ts=json.loads((OUT/f'{gid}-turns.json').read_text()); us=[t for t in ts if t['side']=='us']; qt=[t for t in us if t['id']==g['queen_ids']['us']]
    index={(t['round'],t['id']):t for t in ts}
    W,H=map(int,base['text'].splitlines()[0].split()[1:3])
    def distance(a,b):
        dx,dy=abs(a[0]-b[0]),abs(a[1]-b[1]); return min(dx,W-dx)+min(dy,H-dy)
    for t in us:
        if t['end_body'] and t['head']==t['end_body'][0] and not t['split']: add('surviving_stationary_unsplit',g,t)
        if t['action']==2 and 350<t['round']<=400 and t['count']>=56: add('FEED_CAP_signature',g,t)
        if t['length']>=8 and t['id']!=g['queen_ids']['us'] and not t['split'] and 2<=len(t['steps'])<=min(6,(t['length']+3)//4) and t['enemy_heads']:
            add('BIG_ESCAPE_multistep_exposure',g,t)
        if t['id']!=g['queen_ids']['us'] and t['length']<4 and t['head_portal_dirs'] and t['steps'] and t['dirs'][0] not in t['head_portal_dirs'] and len(t['free'])>=2:
            add('PORTAL_SCOUT_ordinary_choice',g,t)
    longhits=[d for d in base['deaths'] if d['side']=='us' and d['length']>=8 and d['reason']==3 and d['actor']!=d['id']]
    for d in longhits:
        t=index[(d['round'],d['actor'])]
        add('long_dragon_rammed',g,dict(round=d['round'],id=d['id'],head=d['body'][0]))
        d['attacker_start']=dict(id=t['id'],length=t['length'],head=t['head'],steps=t['steps'],dirs=t['dirs'])
    suicides=[d for d in base['deaths'] if d['side']=='us' and d['reason']==4]
    dd={d['death'] for d in suicides}; drops=[p for p in base['pearls'] if p['death'] in dd]
    suicide_recovery=Counter(p['eater'] for p in drops)
    for d in suicides:
        if not any(p['death']==d['death'] and p['eater']=='us' for p in drops): add('suicide_no_ally_recovery',g,dict(round=d['round'],id=d['id'],head=d['body'][0]))
    root=lr.replay.load(path).root(); key=codec.make_key(W,H,codec.team_tag(g['ours'])); streams={}; opened={}; rnd=0
    fars=[]
    for ev in root.pointer(3):
        k=ev.u16(0); p=ev.pointer(0)
        if k==0:rnd=p.i32(0)
        elif k==12:
            wire=p.u64(16)
            if ((wire>>53)&3)!=codec.team_tag(g['ours']): continue
            if wire not in opened: opened[wire]=codec.unseal(key,wire,streams)
            plain=opened[wire]
            if plain is None or not plain>>63 or ((plain>>38)&0x7fff)!=0x5b:continue
            hit=p.i32(12) if p.u16(6) else None
            msg=dict(round=rnd,id=p.i32(0),hit=hit,cell=plain&0x3fff,parts=((plain>>14)&0x3fff)+1,when=(plain>>28)&0x1ff)
            fars.append(msg);add('QUEEN_FAR_HEADS_sent',g,msg)
            if hit==g['queen_ids']['us']:
                add('QUEEN_FAR_HEADS_hits_queen',g,msg)
    finalq=g['final']['us']['queen_length']; losealive=[(int(r),st) for r,st in g['snapshots'].items() if st['them']['queen_length']>st['us']['queen_length']]
    closest = max(losealive,key=lambda x:x[0],default=None)
    detail=dict(gid=gid,map=g['map'],last_queen_deficit=closest,adjacent_threats=g['queen_adjacent_enemy_turns'],queen_last_turns=qt[-3:],
                longhits=longhits,suicide_recovery=dict(suicide_recovery),suicide_drops=len(drops),far_messages=fars,
                queen_splits=[s for s in g['splits'] if s['parent']==g['queen_ids']['us']],
                pearl100=g['snapshots'].get('100',g['snapshots'].get(100)),queen_ram=g['queen_deaths'],rams=g['rams'])
    details.append(detail)
    print(gid,'deficit',closest,'qthreat',g['queen_adjacent_enemy_turns'][:3],'longhits',[(d['round'],d['id'],d['length'],d['attacker_start']['length']) for d in longhits], 'far',len(fars), 'suicide recovery',dict(suicide_recovery),flush=True)
audit['FEED_CAP_ROUND_compatible']=dict(count=totals['FEED_CAP_signature'],games=len(games['FEED_CAP_signature']),examples=moments['FEED_CAP_signature'])
audit['code_reference']='data/online/smoke/one12-bot/main.cpp'
audit['note']='12 own bot ids21330. Signatures/exposures are not isolated switch activations. Far-head messages decoded using shipped codec; receipt hit records do not prove a changed move.'
(OUT/'switch-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
(OUT/'details.json').write_text(json.dumps(dict(games=details,totals=dict(totals),moments=dict(moments),game_counts={k:len(v) for k,v in games.items()}),ensure_ascii=False,separators=(',',':')))
print('TOTAL',dict(totals),flush=True)

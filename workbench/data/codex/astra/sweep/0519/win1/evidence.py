import sys
sys.dont_write_bytecode=True
import json, gzip
from pathlib import Path
from collections import defaultdict,deque
sys.path.insert(0,'tools')
from ladder_replay import replay,edge_id,canonical_edges
OUT=Path('data/codex/astra/sweep/0519/win1')
rows=[]
for gid in (1491740,1492100,1492101,1492105):
    plain=OUT/f'{gid}.json'
    x=json.loads(plain.read_text()) if plain.exists() else json.loads(gzip.decompress((OUT/f'{gid}.json.gz').read_bytes()))
    b,d=x['base'],x['detail'];q=d['queens'][0];qt=[t for t in d['turns'] if t['id']==q]
    root=replay.load(Path(b['folder'])/f'M{gid}.replay').root()
    w,h=d['w'],d['h']
    edges=canonical_edges(w,h,[tuple(map(int,l.split()[1:4])) for l in root.text(0).splitlines() if l.startswith('EDGE ')])
    portals=defaultdict(list)
    for e,(kind,pid) in edges.items():
        if kind==2:portals[pid].append(e)
    def step(pos,dire):
        e=edge_id(w,h,*pos,dire);kind,pid=edges.get(e,(0,-1))
        if kind==1:return None
        if kind==2:
            other=next(z for z in portals[pid] if z!=e);row,px=divmod(other,w+1)
            return ((px-(dire==3))%w,(row//2-(dire==0))%h)
        dx,dy=((0,-1),(1,0),(0,1),(-1,0))[dire]
        return ((pos[0]+dx)%w,(pos[1]+dy)%h)
    reached={tuple(qt[0]['start'])};queue=deque(reached)
    while queue:
        pos=queue.popleft()
        for dire in range(4):
            nxt=step(pos,dire)
            if nxt is not None and nxt not in reached:reached.add(nxt);queue.append(nxt)
    portal_adjacent=[];portal_crossings=[]
    for t in qt:
        if any(edges.get(edge_id(w,h,*t['start'],dire),(0,-1))[0]==2 for dire in range(4)):portal_adjacent.append(t['r'])
        pos=tuple(t['start'])
        for dire in t['dirs']:
            if edges.get(edge_id(w,h,*pos,dire),(0,-1))[0]==2:portal_crossings.append(t['r'])
            pos=step(pos,dire)
            if pos is None:break
    deaths={z['death']:z for z in b['deaths']}
    bootstrap=[]
    for pr in b['pearls']:
        z=deaths[pr['death']]
        if z['side']=='us' and z['reason']==4 and pr['eater_id']==q:
            t=next(t for t in qt if t['r']==pr['eat_round'])
            if t['length']<6:bootstrap.append(dict(donor=z['id'],donor_length=z['length'],stop_round=z['round'],eat_round=pr['eat_round'],queen_start_length=t['length'],xy=pr['xy']))
    cuts=[dict(round=t['r'],enemy=z['id'],observed=z['parts'],actual=z['length']) for t in qt for z in t['heads'] if z['side']==1 and z['visible'] and z['cut'] and z['parts']<4]
    stops=[t for t in d['turns'] if t['side']==0 and any(z['id']==t['id'] and z['reason']==4 for z in t['deaths'])]
    misses=[t for t in d['turns'] if t['side']==0 and t['adj_pearls'] and not t['eaten'] and t['split'] is None and not t['deaths']]
    qram=[t for t in d['turns'] if t['side']==0 and any(z['id']==d['queens'][1] and z['reason']==3 for z in t['deaths'])]
    rows.append(dict(gid=gid,bot=b['bots']['A'],queens=d['queens'],final=b['final'],last_round=b['last_round'],permanent_ahead=d['permanent_ahead'],bootstrap=bootstrap,cut_inputs=len(cuts),cut_moments=cuts[:3],stop_count=len(stops),first_stops=[{k:t[k] for k in ('r','id','length','units','queen_lengths')} for t in stops[:3]],adjacent_pearl_miss_turns=len(misses),miss_moments=[{k:t[k] for k in ('r','id','length','start','end','dirs','adj_pearls')} for t in misses[:3]],our_enemy_queen_rams=len(qram),logs=d['logs'],queen_stationary_without_split=sum(t['start']==t['end'] and t['split'] is None for t in qt)))
    rows[-1].update(queen_component_size=len(reached),queen_portal_adjacent_rounds=portal_adjacent,queen_portal_crossing_rounds=portal_crossings,queen_eaten_after_round1=sum(len(t['eaten']) for t in qt if t['r']>1))
totals=dict(games=len(rows),bootstrap_games=sum(bool(r['bootstrap']) for r in rows),bootstrap_pearls=sum(len(r['bootstrap']) for r in rows),cut_input_games=sum(r['cut_inputs']>0 for r in rows),cut_inputs=sum(r['cut_inputs'] for r in rows),stops=sum(r['stop_count'] for r in rows),adjacent_pearl_miss_turns=sum(r['adjacent_pearl_miss_turns'] for r in rows),our_enemy_queen_rams=sum(r['our_enemy_queen_rams'] for r in rows))
totals.update(queen_portal_adjacent_turns=sum(len(r['queen_portal_adjacent_rounds']) for r in rows),queen_portal_adjacent_games=sum(bool(r['queen_portal_adjacent_rounds']) for r in rows),queen_portal_crossings=sum(len(r['queen_portal_crossing_rounds']) for r in rows))
(OUT/'evidence.json').write_text(json.dumps(dict(totals=totals,games=rows),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(totals=totals,games=rows),ensure_ascii=False,indent=2))

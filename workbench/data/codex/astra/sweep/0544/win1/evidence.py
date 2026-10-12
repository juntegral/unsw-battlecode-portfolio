import sys
sys.dont_write_bytecode=True
import json,gzip
from pathlib import Path
from collections import Counter
sys.path.insert(0,'tools')
import ladder_replay as lr
OUT=Path(__file__).parent
rows=[]
for gid in (1493877,1493885,1493887,1493889):
    x=json.loads(gzip.decompress((OUT/f'{gid}.json.gz').read_bytes()));b,d=x['base'],x['detail'];q,eq=d['queens'];ts=[t for t in d['turns'] if t['side']==0];qt=[t for t in ts if t['id']==q]
    stops=[z for z in b['deaths'] if z['side']=='us' and z['reason']==4]
    stopids={z['death'] for z in stops}
    fed=[p for p in b['pearls'] if p['death'] in stopids and p['eater_id']==q]
    misses=[t for t in ts if t['adj_pearls'] and not t['eaten'] and not t['split'] and not t['deaths']]
    small=[dict(round=t['r'],actor=t['id'],enemy=z['id'],visible_parts=z['parts'],actual=z['length']) for t in ts if t['id']!=q and t['length']<=4 for z in t['heads'] if z['side']==1 and z['visible'] and 3<=z['parts']<=4]
    root=lr.replay.load(Path(b['folder'])/f'M{gid}.replay').root()
    edges=lr.canonical_edges(d['w'],d['h'],[tuple(map(int,l.split()[1:4])) for l in root.text(0).splitlines() if l.startswith('EDGE ')])
    pp=[(e,pid) for e,(kind,pid) in edges.items() if kind==2]
    row=dict(gid=gid,bot=b['bots']['A'],queens=d['queens'],last_round=b['last_round'],final=b['final'],permanent_ahead=d['permanent_ahead'],logs=d['logs'],anomalies=b['anomalies'],q_deaths=[z for z in b['deaths'] if z['id'] in (q,eq)],stops=len(stops),stop_segments=sum(z['length'] for z in stops),stop_drops=sum(len(z['pearls']) for z in stops),stop_drops_to_queen=len(fed),stop_drop_examples=fed[:3],adjacent_pearl_eaten_turns=sum(any(c in t['eaten'] for c in t['adj_pearls']) for t in ts),adjacent_pearl_miss_turns=len(misses),miss_moments=[{k:t[k] for k in ('r','id','length','start','end','dirs','adj_pearls')} for t in misses[:3]],stationary_without_split=sum(t['start']==t['end'] and not t['split'] for t in ts),queen_L4_no_split_units2=sum(t['length']==4 and t['units'][0]>=2 and t['split'] is None for t in qt),small_sprint_threat_input_pairs=len(small),small_sprint_examples=small[:3],ram_enemy_queen=[{k:t[k] for k in ('r','id','length','start','dirs','deaths','queen_lengths','units','heads')} for t in ts if any(z['id']==eq and z['reason']==3 for z in t['deaths'])],portal_edge_count=len(pp),portal_id_guard_inputs=sum(pid>=2*d['w']*d['h'] for e,pid in pp),unit_cap_feed_input_turns=sum(t['r']>350 and t['units'][0]>=56 for t in ts))
    row['selected_rounds']={r:st for r,st in d['rounds'].items() if int(r) in (14,38,39,52,53,54,86,87,100,300,335,336,354,355,400,401,410,414,419,420,499)}
    rows.append(row)
totals={k:sum(r[k] for r in rows) for k in ('stops','stop_segments','stop_drops','stop_drops_to_queen','adjacent_pearl_eaten_turns','adjacent_pearl_miss_turns','stationary_without_split','queen_L4_no_split_units2','small_sprint_threat_input_pairs','portal_edge_count','portal_id_guard_inputs','unit_cap_feed_input_turns')}
totals.update(games=len(rows),queen_alive_end=sum(r['final']['us']['queen_alive'] for r in rows),enemy_queen_rams=sum(len(r['ram_enemy_queen']) for r in rows),small_input_games=sum(r['small_sprint_threat_input_pairs']>0 for r in rows),portal_games=sum(r['portal_edge_count']>0 for r in rows))
(OUT/'evidence.json').write_text(json.dumps(dict(totals=totals,games=rows),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(totals=totals,examples=[dict(gid=r['gid'],small=r['small_sprint_examples'][:1],portals=r['portal_edge_count'],capturns=r['unit_cap_feed_input_turns']) for r in rows]),ensure_ascii=False,indent=2))

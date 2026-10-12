import json,csv
from pathlib import Path
from collections import Counter,defaultdict
from statistics import mean
OUT=Path(__file__).resolve().parent
VERS=('one5','one7','one8','one9','one10')
def write(name,rows):
 if not rows:return
 keys=list(dict.fromkeys(k for x in rows for k in x))
 with (OUT/name).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=keys,delimiter='\t');wr.writeheader()
  for r in rows:wr.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()})
def main():
 inv=json.loads((OUT/'inventory.json').read_text());ids={r['gid'] for r in inv['rows']};gs=[json.loads(p.read_text()) for p in OUT.glob('game-*.json') if int(p.stem[5:]) in ids];gs.sort(key=lambda g:g['gid'])
 summaries={};misses=[];hits=[];queen=[];feeds=[];late=[];rally=[];moments=[]
 for g in gs:
  key=dict(version=g['version'],gid=g['gid'],map=g['map'],result=g['result'],how=g['how']);end=g['snaps']['end']
  for t in g['reach']:
   if not t['hitqueen']:misses.append(dict(**key,**t,reason_status='code gates reconstructed; internal memory unavailable'))
  for d in g['deaths']:
   if d['queen'] and d['side']==1:
    ra=d.get('rammer');hit=dict(**key,round=d['r'],cause=d['cause'],rammer=ra,our_final_queen=end[0][3],their_final_queen=end[1][3],our_final_longest=end[0][2],their_final_longest=end[1][2],result_changed='counterfactual unmeasured')
    if ra:
     donor=next(x for x in g['deaths'] if x['id']==ra['id'] and x['r']==d['r'])
     hit.update(gross_dragon_length_cost=ra['L'],death_length=donor['L'],paid_before_hit=ra['paid_before_hit'],paid_intended=max(0,ra['steps']-ra['free_steps']),our_body_recovered_by_us=sum(t['side']==0 for t in donor['eaters']),our_body_eaten_by_enemy=sum(t['side']==1 for t in donor['eaters']),queen_body_eaten_by_us=sum(t['side']==0 for t in d['eaters']))
    elif d['cause']=='rams':
     hit['enemy_queen_initiated']=True
     hit['our_stationary_victim']=[dict(id=x['id'],L=x['L'],steps=0) for x in g['deaths'] if x['side']==0 and x['r']==d['r'] and x['actor']==d['id'] and x['cause']=='rammed']
    hits.append(hit)
  queen.append(dict(**key,our_q300=g['snaps'].get('300',[None,None])[0],our_q400=g['snaps'].get('400',[None,None])[0],end_our=end[0][3],end_theirs=end[1][3],both=end[0][3]>0 and end[1][3]>0,queen_fed=sum(t['side']==0 and t['source_side']==0 and t['queen'] for t in g['transfers']),queen_stop_fed=sum(t['side']==0 and t['source_side']==0 and t['queen'] and t['cause']=='stop' for t in g['transfers'])))
  for t in g['transfers']:
   if t['side']==0 and t['queen']:feeds.append(dict(**key,**t))
  ds=[d for d in g['deaths'] if d['side']==0 and d['r']>=350];ts=[t for t in g['transfers'] if t['source_side']==0 and t['death_r']>=350]
  stops=[d for d in ds if d['cause']=='stop'];stopts=[t for t in ts if t['cause']=='stop']
  late.append(dict(**key,corpse_mass=sum(d['L'] for d in ds),pearls_dropped=sum((d['L']+1)//2 for d in ds),to_top=sum(t['side']==0 and t['top'] for t in ts),to_mates=sum(t['side']==0 for t in ts),to_enemy=sum(t['side']==1 for t in ts),unconsumed=sum((d['L']+1)//2 for d in ds)-len(ts),stop_mass=sum(d['L'] for d in stops),stop_dropped=sum((d['L']+1)//2 for d in stops),stop_to_top=sum(t['side']==0 and t['top'] for t in stopts),stop_to_mates=sum(t['side']==0 for t in stopts),stop_to_enemy=sum(t['side']==1 for t in stopts)))
  for c in g['candidates']:rally.append(dict(**key,**c))
 for v in VERS:
  xs=[g for g in gs if g['version']==v];n=len(xs)
  if not n:summaries[v]={'n':0};continue
  end=[g['snaps']['end'] for g in xs];qdeath=[d for g in xs for d in g['deaths'] if d['side']==1 and d['queen']];qrams=[d for d in qdeath if 'rammer'in d];mts=[r for r in misses if r['version']==v];rs=[r for r in rally if r['version']==v];ls=[r for r in late if r['version']==v];fs=[r for r in feeds if r['version']==v];qt=[t for g in xs for t in g['qturns'] if 51<=t['r']<=300]
  finalboth=[e for e in end if e[0][3]>0 and e[1][3]>0]
  summaries[v]=dict(n=n,revision_counts=dict(Counter(g.get('revision',1) for g in xs)),opponents=dict(Counter(g['opponent'] for g in xs)),queen_dead=len(qdeath),queen_ram=len(qrams),queen_ram_paid=sum(d['rammer']['steps']>d['rammer']['free_steps'] for d in qrams),queen_ram_cost=sum(d['rammer']['L'] for d in qrams),queen_ram_cost_max=max((d['rammer']['L'] for d in qrams),default=0),missed=len(mts),missed_visible=sum(t['visible'] for t in mts),missed_unresolved=sum('unresolved_internal_memory_or_override' in t['reasons'] for t in mts),missed_reasons=dict(Counter(r for t in mts for r in t['reasons'])),q300=[sum(g['snaps']['300'][0][3] for g in xs if '300'in g['snaps']),sum('300'in g['snaps'] for g in xs)],q400=[sum(g['snaps']['400'][0][3] for g in xs if '400'in g['snaps']),sum('400'in g['snaps'] for g in xs)],qend=sum(e[0][3] for e in end)/n,qalive=sum(e[0][3]>0 for e in end),both=len(finalboth),both_ours_longer=sum(e[0][3]>e[1][3] for e in finalboth),both_tie=sum(e[0][3]==e[1][3] for e in finalboth),both_theirs_longer=sum(e[0][3]<e[1][3] for e in finalboth),queen_mate_pearls=sum(t['source_side']==0 for t in fs),queen_stop_pearls=sum(t['source_side']==0 and t['cause']=='stop' for t in fs),qboot_pearls=sum(t['source_side']==0 and t['cause']=='stop' and t['eaterL']<6 and t['sourceL'] in (2,3) for t in fs),q_isolation=[sum(t['mate5']==0 for t in qt),len(qt)],longest_games=sum(g['how']=='longest' for g in xs),longest_losses=sum(g['how']=='longest' and g['result']=='loss' for g in xs),late={k:sum(r[k] for r in ls) for k in ('corpse_mass','pearls_dropped','to_top','to_mates','to_enemy','unconsumed','stop_mass','stop_dropped','stop_to_top','stop_to_mates','stop_to_enemy')},rally={k:sum(r[k] for r in rs) for k in ('L','lost','remaining','ever_top','end_top','inward','moves')},rally_n=len(rs),rally_bad_ratio=sum(not r.get('actual_ratio_ok',True) for r in rs),rally_dead_leader=sum(r.get('actual_leaderL',1)==0 for r in rs),rally_arrival=sum(r['arrival'] is not None for r in rs),rally_death_before_arrival=sum(r['death'] is not None and (r['arrival'] is None or r['death'][0]<r['arrival'][0]) for r in rs),state_messages=dict(sum((Counter(g['states']) for g in xs),Counter())),qavenge_logs=sum(g['logs'].get('QAVENGE',0) for g in xs),truncated=sum(g['coverage'].get('path_search_truncated',0) for g in xs))
 for name,rows in [('missed-turns.tsv',misses),('queen-deaths.tsv',hits),('queen-lengths.tsv',queen),('queen-transfers.tsv',feeds),('late-mass.tsv',late),('rally-cohorts.tsv',rally)]:write(name,rows)
 (OUT/'summary.json').write_text(json.dumps(summaries,ensure_ascii=False,indent=2));print(json.dumps(summaries,ensure_ascii=False,indent=2))
if __name__=='__main__':main()

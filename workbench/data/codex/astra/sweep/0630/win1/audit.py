import sys,json
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
OUT=Path(__file__).resolve().parent
rows=json.loads((OUT/'measurements.json').read_text())
counts=Counter();examples={};games={}
def add(k,g,t):
 counts[k]+=1;examples.setdefault(k,[]);games.setdefault(k,set()).add(g['gid'])
 if len(examples[k])<3:examples[k].append(dict(game=g['gid'],round=t['round'],dragon=t['id']))
for g in rows:
 ts=json.loads((OUT/f"{g['gid']}-turns.json").read_text());us=[t for t in ts if t['side']=='us']
 for t in us:
  if t['steps'] and t['steps'][0] in t['pearl_adj']:add('EAT_FIRST_adjacent_eat',g,t)
  if t['pearl_adj'] and t['steps'] and t['steps'][0] not in t['pearl_adj'] and not t['deaths']:add('adjacent_pearl_passed',g,t)
  if t['round']<12 and t['dirs'] and len(t['body'])>=2 and t['adj'][(t['dirs'][0]+2)%4]==t['body'][1]:add('HEADING_TIE_forward',g,t)
  if t['split'] and t['id']!=g['queen_ids']['us'] and t['length']==4 and t['round']<=100 and t['tail_portal']:add('SPLIT_PORTAL_OK_candidate',g,t)
  if t['id']==g['queen_ids']['us'] and t['split'] and t['count']<6 and t['length']==4 and len(t['end_body'])==2:add('QS_KEEP_MIN_UNITS_below6_to2',g,t)
  if any(3<=e['visible']<=4 for e in t['visible_enemy_parts']):add('SMALL_SPRINT_THREAT_exposure',g,t)
  if t['id']==g['queen_ids']['us']:
   if any(e['edge'] and e['visible']<4 for e in t['visible_enemy_parts']):add('CUT_BODY_exposure',g,t)
   if t['dirs'] and t['dirs'][0] in t['head_portal_dirs']:add('QUEEN_PORTAL_LAST_crossing',g,t)
  if t['action']==2:add('no_action_death',g,t)
 for r in g['rams']:
  t=next(t for t in us if t['round']==r['round'] and t['id']==r['actor'])
  if r['queen_target']:add('QUEEN_SURE_compatible',g,t)
  if r['queen_dist'] is not None and r['queen_dist']<=3 and not r['queen_target'] and any(i==g['queen_ids']['us'] for i,c in t['mate_heads']) and any(i==r['target'] for i,c,l in t['enemy_heads']):add('QUEEN_DEFEND_compatible',g,t)
definitions={
'EAT_FIRST_adjacent_eat':'First successful step enters a currently empty adjacent pearl tile, including portal adjacency; safety predicates and competing scores not reproduced.',
'adjacent_pearl_passed':'Survives turn, first step does not enter any currently unoccupied adjacent pearl tile; may be unsafe, ineligible or eaten later this turn.',
'HEADING_TIE_forward':'First requested move at r0-11 faces away from current neck, using actual canonical adjacency; no score tie verified.',
'SPLIT_PORTAL_OK_candidate':'Non-queen splits at L4 by r100, actual tail touches a portal. Escape split and sonar-dependent predicates not distinguished.',
'QS_KEEP_MIN_UNITS_below6_to2':'Queen splits L4 to L2 with team count below6; primary/escape split branch not established.',
'SMALL_SPRINT_THREAT_exposure':'An enemy head in actor view has3 or4 actual segments in view; no chosen-move effect asserted.',
'CUT_BODY_exposure':'Queen sees enemy head with fewer than4 body cells in view, at least one visible enemy cell on her view edge. Includes enemy queen; does not reproduce memory.',
'QUEEN_PORTAL_LAST_crossing':'Queen first move crosses an actual portal; no claim that the unseen emergency fallback ran.',
'QUEEN_SURE_compatible':'Our non-queen initiates head ram killing their queen. Leader state and overlapping trade/hunt branches not reconstructed.',
'QUEEN_DEFEND_compatible':'Our ram victim is a non-queen within3 topology steps of our queen, actor sees both queen and victim at turn start; does not establish unique guard branch.',
'no_action_death':'Action discriminant2: no-action suicide, not a surviving idle turn.'}
audit={k:dict(count=counts[k],games=len(games.get(k,set())),examples=examples.get(k,[]),definition=v) for k,v in definitions.items()}
audit['QUEEN_HERD_compatible']=dict(count=sum(g['counts']['herd_compatible'] for g in rows),games=sum(g['counts']['herd_compatible']>0 for g in rows),examples=[dict(game=g['gid'],round=t['round'],dragon=t['id']) for g in rows for t in g['examples']['herd'][:1]],definition='Queen has >=12 teammates, exactly one visible mate, moves closer to it from Manhattan distance>3; topology, remembered mates, leader status and score cause not reproduced.')
audit['QUEEN_BOOT_LEN_compatible']=dict(count=sum(g['counts']['boot_feeding_compatible'] for g in rows),games=sum(g['counts']['boot_feeding_compatible']>0 for g in rows),examples=[dict(game=g['gid'],round=t['round'],dragon=t['id']) for g in rows for t in g['examples']['feed']],definition='After r400, L2/3 ally with short living queen within torus Manhattan3 chooses suicide; leader sonar target unknown.')
audit['FEED_CAP_ROUND_compatible']=dict(count=1,games=1,examples=[dict(game=1496854,round=351)],definition='Schooltime first no-action death at351, team61 at end350; Islands first stop327 under other feeding trigger, so not credited to cap.')
audit['PORTAL_ID_GUARD_high_id_exposure']=dict(count=sum(len(g['high_portal_ids']) for g in rows),games=sum(bool(g['high_portal_ids']) for g in rows),definition='Distinct actual portal ids>=2*cells. Does not check whether queen/mates observed every edge.')
audit['unknown_attribution']=['QUEEN_DEAD_ALL','QUEEN_EXIT_KEEP','QUEEN_AVENGE','MATE_UNPIN','POCKET_KEEP_OUT','TARGET_REACHABLE','REACH_EATS','QUEEN_EXIT_STRICT']
audit['code_reference']='data/online/smoke/one11-bot/main.cpp'
audit['note']='All are measured signatures/exposures, not isolated switch activation counts. All8 own bot ids21269; engine and dragon log event counts0. No games or bot executions.'
(OUT/'switch-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
print(json.dumps(audit,ensure_ascii=False,indent=2))

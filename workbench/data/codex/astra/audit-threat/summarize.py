import sys
sys.dont_write_bytecode=True
import json,gzip,math,random
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime
OUT=Path(__file__).resolve().parent
CLASSES=['one_free','several_free','paid','pearls_on_way','view_cut','unseen']

def load_games():
 inv=json.loads((OUT/'inventory.json').read_text())
 return [json.loads((OUT/f'g{j["gid"]}.json').read_text()) for j in inv['games'] if (OUT/f'g{j["gid"]}.json').exists()]

def percentile(hist,q):
 n=sum(hist.values());at=max(1,math.ceil(n*q));s=0
 for k,v in sorted(hist.items()):
  s+=v
  if s>=at:return k

def combined(gs):
 c=Counter();lens=Counter();rr={x:Counter() for x in ('q','other')};qd=Counter();fates=Counter();portals=[];unknown_food=0
 for g in gs:
  c.update(g['counts']);lens.update({int(k):v for k,v in g['qlens'].items()})
  for r in g['rams']:
   v=rr['q' if r['q'] else 'other'];v['all']+=1
   # Movement bands are mutually exclusive. Pearl/view diagnostics overlap them.
   v['one_free' if r['steps']==1 else 'several_free' if r['steps']<=r['free'] else 'paid']+=1
   v['pearls_on_way']+=r['ate']>0;v['pearl_extended']+=r['pearl_extended'];v['view_cut']+=r['view_cut'];v['unseen']+=r['reach_class']=='unseen'
  for d in g['deaths']:
   if d['q']:qd[d.get('reach_class','unknown')]+=1
  for f in g['fates']:fates[f['tag']+'_'+f['next5']]+=1
 rates={k:{cl:round(1000*v[cl]/c['queen_turns' if k=='q' else 'other_turns'],4) if c['queen_turns' if k=='q' else 'other_turns'] else None for cl in ['all']+CLASSES+['pearl_extended']} for k,v in rr.items()}
 return dict(games=len(gs),ids=[g['gid'] for g in gs],counts=dict(c),ram_counts={k:dict(v) for k,v in rr.items()},ram_rates=rates,queen_death_classes=dict(qd),queen_length_quantiles=[percentile(lens,q) for q in (.1,.25,.5,.75,.9)],queen_length_hist=dict(lens),queen_end=[g['qfinal'] for g in gs],short_pearls_per_turn=c['short_pearls']/c['short_turns'] if c['short_turns'] else None,queen_pearls_per_turn=c['queen_pearls']/c['queen_turns'] if c['queen_turns'] else None,queen_not_toward_food_fraction=c['queen_not_toward_food']/c['queen_food_known_turns'] if c['queen_food_known_turns'] else None,logs=dict(sum((Counter(g['logs']) for g in gs),Counter())),fates=dict(fates))

def main():
 gs=load_games();groups={}
 for v in (5,7,8,9,10):
  groups[f'one{v}']=combined([g for g in gs if g['v']==v])
  for opp in ('WeHaveQuizzes','Cache me outside','kraken'):
   groups[f'one{v}:{opp}']=combined([g for g in gs if g['v']==v and g['opp']==opp])
 groups['before']=combined([g for g in gs if g['v'] in (5,7)])
 groups['after']=combined([g for g in gs if g['v'] in (8,9,10)])
 groups['one9+10']=combined([g for g in gs if g['v'] in (9,10)])
 (OUT/'summary.json').write_text(json.dumps(dict(at=datetime.now().astimezone().isoformat(),groups=groups),ensure_ascii=False,indent=2))
 for key in ['before','after','one5','one7','one8','one9','one10','one8:kraken','one9:kraken','one10:kraken']:
  x=groups[key];print(key,'n',x['games'],'turns',x['counts'].get('other_turns'),x['counts'].get('queen_turns'),'ram/1000',x['ram_rates'],'qdead',x['queen_death_classes'],'food',x['short_pearls_per_turn'],x['queen_pearls_per_turn'],'qlens',x['queen_length_quantiles'],'notfood',x['queen_not_toward_food_fraction'])
 print('QUEEN DEATHS')
 for g in gs:
  if g['v'] not in (9,10):continue
  for d in g['deaths']:
   if not d['q']:continue
   r=next((r for r in g['rams'] if r['q']),None)
   print(g['gid'],g['v'],g['map'],d['r'],d.get('reach_class'),d['L'],dict((k,r[k]) for k in ('steps','free','ate','attacker_L','visible_parts','last_turn','born_after_decision')) if r else '')
if __name__=='__main__':main()

import sys,json,csv
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter,defaultdict
OUT=Path(__file__).resolve().parent
LABELS=('one5-w1','one5-c1','one7-w1','one7-c1')
games=[json.loads(p.read_text()) for p in sorted(OUT.glob('scan-*.json'))]
for g in games:
 for t in g['turns']:
  t['change_compatible']=t['free_window'] and t['endpoint'] is not None and not t['chosen_free']
tables=json.loads((OUT/'table-rows.json').read_text());s={};allrams=[];cohorts=[]

def classify(r):
 t=r['turn']
 if t is None:return 'no_prior_turn'
 if t['kind']==1:return 'exempt_split'
 if t['kind']!=0 or not t['dirs']:return 'exempt_stop'
 if t['attack_path']:return 'exempt_attack_path'
 if t['L']>4:return 'length>4'
 if t['leader'] is True:return 'leader'
 if t['heads'][0]>t['heads'][1]:return 'ahead_in_heads'
 if t['leader'] is None:return 'leader_unresolved'
 if not r['visible_attacker']:return 'attacker_not_visible'
 if not r['attacker_free_reaches']:return 'attacker_outside_free_reach'
 if not t['chosen_danger']:return 'ally_closer_exception'
 if not any(c['room'] and not c['free'] for c in t['choices']):return 'no_certified_safe_alternative'
 return 'would_veto_unresolved_scores_or_override'

def outcome(ts):return dict(n=len(ts),outcomes=dict(Counter(t['outcome'] for t in ts)),ate5=sum(t['ate5']>0 for t in ts),pearls5=sum(t['ate5'] for t in ts))
for label in LABELS:
 gs=[g for g in games if g['label']==label];ts=[t for g in gs for t in g['turns']];rs=[r for g in gs for r in g['rams']];tabs=[r for r in tables if r['label']==label]
 z=dict(games=len(gs),turns=len(ts),turns200=sum(t['round']<=200 for t in ts),nonqueen_turns200=sum(t['round']<=200 and t['id']>1 for t in ts),table=dict(Counter(r['status'] for r in tabs)),rams=len(rs),classes=dict(Counter(classify(r) for r in rs)),classes200=dict(Counter(classify(r) for r in rs if r['round']<=200)))
 z['paid_rams']=sum(r['paid_attack'] for r in rs);z['paid_rams200']=sum(r['paid_attack'] for r in rs if r['round']<=200)
 z['eligible_rams']=sum(bool(r['turn'] and r['turn']['eligible']) for r in rs)
 for cohort in ('eligible','free_window','change_compatible','plus_window'):
  z[cohort]=outcome([t for t in ts if t[cohort]])
  z[cohort+'200']=outcome([t for t in ts if t[cohort] and t['round']<=200])
 z['safe_fraction_in_window']=sum(t['change_compatible'] for t in ts)
 z['chosen_danger_in_window']=sum(t['free_window'] and t['chosen_danger'] for t in ts)
 z['added_plus_rams']=sum(r['turn'] is not None and r['turn']['eligible'] and not r['turn']['chosen_free'] and r['attacker_plus_reaches'] and any(c['room'] and not c['plus'] for c in r['turn']['choices']) for r in rs)
 z['added_plus_rams200']=sum(r['round']<=200 and r['turn'] is not None and r['turn']['eligible'] and not r['turn']['chosen_free'] and r['attacker_plus_reaches'] and any(c['room'] and not c['plus'] for c in r['turn']['choices']) for r in rs)
 z['compatible_rams']=dict(Counter(('paid' if r['paid_attack'] else 'unseen' if not r['visible_attacker'] else 'other') for r in rs if r['turn'] and r['turn']['change_compatible']))
 z['length_hist']=dict(Counter(r['turn']['L'] if r['turn'] else 'no prior' for r in rs))
 z['rules_exempt_overlap']=dict(split=sum(bool(r['turn'] and r['turn']['kind']==1) for r in rs),stop=sum(bool(r['turn'] and (r['turn']['kind']!=0 or not r['turn']['dirs']) and r['turn']['kind']!=1) for r in rs),attack=sum(bool(r['turn'] and r['turn']['attack_path']) for r in rs))
 s[label]=z
 for g in gs:
  for r in g['rams']:
   t=r['turn'];rec={k:v for k,v in r.items() if k!='turn'};rec['class']=classify(r)
   if t:
    for k in ('event','round','L','head','heads','leader','leader_possible','kind','dirs','queen_visible','eligible','free_window','change_compatible','chosen_free','chosen_danger','chosen_plus','plus_window','endpoint','dead5','ate5'):
     rec['turn_'+k]=t.get(k)
    rec['added_plus']=t['eligible'] and not t['chosen_free'] and r['attacker_plus_reaches'] and any(c['room'] and not c['plus'] for c in t['choices'])
    rec['safe_options']=[c for c in t['choices'] if c['room'] and not c['free']]
    rec['plus_safe_options']=[c for c in t['choices'] if c['room'] and not c['plus']]
   allrams.append(rec)
  for t in g['turns']:
   if t['free_window'] or t['plus_window']:
    cohorts.append(dict(label=label,gid=g['gid'],map=g['map'],**{k:t[k] for k in ('event','id','round','L','heads','kind','dirs','free_window','change_compatible','plus_window','chosen_free','chosen_danger','chosen_plus','outcome','ate5','censored5')}))

# Matched strata are descriptive; repeated turns of the same dragon are not independent.
matched={}
for group in ('free_window','change_compatible'):
 for early in (True,False):
  key=lambda t:(t['label'].split('-')[1],t['map'],t['round']//100,t['L'],t['heads'][0]==t['heads'][1])
  b=defaultdict(list);n=defaultdict(list)
  for t in cohorts:
   if t[group] and (not early or t['round']<=200) and t['outcome']!='censored':
    (b if t['label'].startswith('one5') else n)[key(t)].append(t)
  overlap=set(b)&set(n);den=sum(len(n[k]) for k in overlap)
  vals={}
  for name,source in [('one7',n),('one5_standardized',b)]:
   vals[name]={o:sum(len(n[k])*sum(t['outcome']==o for t in source[k])/len(source[k]) for k in overlap)/den if den else None for o in ('dead','alive_ate','alive_no_food')}
  matched[group+('200' if early else '')]=dict(one7_common=den,one7_total=sum(map(len,n.values())),strata=len(overlap),**vals)
(OUT/'summary.json').write_text(json.dumps(dict(labels=s,matched=matched),indent=2))
(OUT/'ram-audit.json').write_text(json.dumps(allrams,separators=(',',':')))
(OUT/'cohorts.json').write_text(json.dumps(cohorts,separators=(',',':')))
for name,rs in [('ram-audit',allrams),('cohorts',cohorts)]:
 fields=list(dict.fromkeys(k for r in rs for k in r))
 with (OUT/(name+'.csv')).open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rs)
print(json.dumps(dict(labels=s,matched=matched),indent=2))

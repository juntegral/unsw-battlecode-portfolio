import json,csv,hashlib,subprocess
from pathlib import Path
from collections import Counter
from statistics import mean
import summarize
OUT=Path(__file__).resolve().parent

def main():
 repaired=json.loads((OUT/'lunge-gate.json').read_text()) if (OUT/'lunge-gate.json').exists() else []
 for path in OUT.glob('game-*.json'):
  g=json.loads(path.read_text());change=False
  for t in g['reach']:
   budget=min((t['L']+3)//4+t['L']-2,5 if g['version']=='one10' else 3)
   if t['sure_path'] and len(t['sure_path'])>budget and (t['units']<56 or t['id']==g['queens'][0]):
    t['sure_path']=None;t['reasons']=[r for r in t['reasons'] if r!='unresolved_internal_memory_or_override'];t['reasons'].append('lunge_pearl_population_gate:3636,4762');change=True
    if not t['hitqueen']:repaired.append(dict(gid=g['gid'],version=g['version'],r=t['r'],id=t['id'],L=t['L'],units=t['units'],path=t['path'],visible=t['visible']))
  if change:path.write_text(json.dumps(g,separators=(',',':'),ensure_ascii=False))
 (OUT/'lunge-gate.json').write_text(json.dumps(repaired,ensure_ascii=False,indent=2));summarize.main()
 gs=[json.loads(p.read_text()) for p in OUT.glob('game-*.json')];inv=json.loads((OUT/'inventory.json').read_text());assert {g['gid'] for g in gs}=={r['gid'] for r in inv['rows']};assert len(gs)==len({g['gid'] for g in gs})
 checks={}
 for v in summarize.VERS:
  xs=[g for g in gs if g['version']==v];cs=[c for g in xs for c in g['candidates']];q=[t for g in xs for t in g['qturns'] if 51<=t['r']<=300]
  wide=[dict(gid=g['gid'],r=d['r'],foeL=d['L'],**d['rammer']) for g in xs for d in g['deaths'] if d.get('rammer') and (d['rammer']['L']>4 or d['rammer']['steps']>3)]
  checks[v]=dict(signal_claim_games=sum(any(int(k)&1 and val>0 for k,val in g['states'].items()) for g in xs),wide=wide,ram_second_longest_lost=[dict(gid=g['gid'],r=d['r'],**d['rammer']) for g in xs if g['how']=='longest' and g['result']=='loss' for d in g['deaths'] if d.get('rammer') and d['rammer']['second_by_id']],cap_boundary=sum(g['snaps'].get('350',[[0]])[0][0]>=56 for g in xs),cap_boundary_n=sum('350'in g['snaps'] for g in xs),candidate_tokens=sum(c['L'] for c in cs),candidate_residuals=sum(c['L']!=c['lost']+c['remaining'] for c in cs),queen_inward=sum(t['end'] is not None and t['head']!=t['end'] for t in q),state_example_games=[g['gid'] for g in xs if any(int(k)&1 and val>0 for k,val in g['states'].items())][:3])
 (OUT/'checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2))
 (OUT/'verification.json').write_text(json.dumps(dict(time=subprocess.check_output(['date','+%Y-%m-%d %H:%M:%S %Z'],text=True).strip(),games=len(gs),final_official_score_checks=2*len(gs),mass_balance_checks=2*len(gs),residual_failures=sum(any(g['checks']) for g in gs),cohort_checks=sum(len(g['candidates']) for g in gs),cohort_residual_failures=sum(c['L']!=c['lost']+c['remaining'] for g in gs for c in g['candidates']),source_sha256={v:hashlib.sha256(Path(f'data/online/smoke/{v}-bot/main.cpp').read_bytes()).hexdigest() for v in summarize.VERS},truncated_searches=sum(g['coverage'].get('path_search_truncated',0) for g in gs)),indent=2))
if __name__=='__main__':main()

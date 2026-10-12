import json,statistics
from pathlib import Path
from collections import Counter,defaultdict
P=Path('data/codex/astra/topqueen2');games={};kills={}
for l in (P/'games.jsonl').read_text().splitlines():
 g=json.loads(l);games[g['gid']]={k:g[k] for k in ['src','teams','version']}
 for k in g['kills']:kills[(g['gid'],k['r'],k['attacker'],k['victim'])]=k
cs=json.loads((P/'convergence.json').read_text());groups=defaultdict(list)
for x in cs:
 g=games[x['gid']];k=kills[(x['gid'],x['r'],x['actor'],x['victim'])];assert set(x['near5'])==set(k['ids5'])
 team=g['teams'][x['side']];key=str(team) if g['src']=='top3' else f"one{g['version']}-{team}";groups[key].append(x)
 if g['src']=='top3':groups['top-all'].append(x)
summary={}
for k,a in groups.items():summary[k]=dict(n=len(a),near_median=statistics.median(len(x['near5']) for x in a),approach_median=statistics.median(len(x['approached3']) for x in a),approach2plus=sum(len(x['approached3'])>=2 for x in a),new_unmeasurable=sum(bool(x['no_previous_turn']) for x in a),dist=dict(Counter(len(x['approached3']) for x in a)))
(P/'convergence-summary.json').write_text(json.dumps(summary,indent=2));v=json.loads((P/'verification.json').read_text());v['convergence_crosscheck']=dict(n=len(cs),near_heads_match=True);(P/'verification.json').write_text(json.dumps(v,indent=2));print('verified',len(cs),'q strikes')

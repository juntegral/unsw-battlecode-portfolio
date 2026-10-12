#!/usr/bin/env python3
"""One additional exploratory model; reuse profiled logistic fitting code only."""
import ast,json,math,collections,time,subprocess,re
from pathlib import Path
R=Path(__file__).resolve().parents[2];C=R/'.cache/outcome-review';last_guard=0
source=ast.parse((R/'exp/outcome-review/analyse-v4.py').read_text())
names={'tcrit','guard','sigmoid','inverse','dot','matmul','model'}
module=ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[])
exec(compile(module,'profiled-logistic-functions','exec'),globals())
G=[json.loads(l)for l in open(C/'games.jsonl')if l.strip()and json.loads(l)['era']=='waves']
for r in G:r['head100ByKelp']=r['headLogRatio100']*(r['layout']['kelpEdges']/r['layout']['edgeCount']/.1) if r['headLogRatio100']is not None else None
z=model(G,['headLogRatio100','head100ByKelp','earlyLogNaturalRatio','waveTrend'])
with open(C/'models-extra.json','x')as f:json.dump({'layout-kelp-interaction':z},f,indent=2);f.write('\n')
print(json.dumps(z))

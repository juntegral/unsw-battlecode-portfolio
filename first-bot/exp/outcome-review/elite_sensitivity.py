#!/usr/bin/env python3
"""Top-six sensitivities only; preserve all original main-model outputs."""
import ast,json,math,collections,time,subprocess,re
from pathlib import Path
R=Path(__file__).resolve().parents[2];C=R/'.cache/outcome-review';last_guard=0
source=ast.parse((R/'exp/outcome-review/analyse-v4.py').read_text())
names={'tcrit','guard','sigmoid','inverse','dot','matmul','model'}
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef)and n.name in names],type_ignores=[]),'profiled-logistic-functions','exec'),globals())
G=[r for r in (json.loads(l)for l in open(C/'games.jsonl')if l.strip())if r['era']=='waves' and r['opponent']!=545]
models={}
models['landmark300-top6']=model([r for r in G if r['rounds']>300],['headLogRatio250','earlyLogNaturalRatio','currentKingDifference300','sacrificeLogRatio300','birthLogRatio300','waveTrend'])
models['late-retrospective-top6']=model(G,['headLogRatio100','headLogRatio250','fullLogNaturalRatio','lineageDifference300','sacrificeLogRatio','lineSacDifference','birthLogRatio','exposureDifference'])
for f in ['headLogRatio100','fullLogNaturalRatio','currentKingDifference300','lineSacDifference','birthLogRatio','exposureDifference']:
    models['elite-single:'+f]=model(G,[f])
with open(C/'models-elite.json','x')as f:json.dump(models,f,indent=2);f.write('\n')
for k,z in models.items():print(k,'N=',z['informativeN'],'converged=',z.get('converged'),'coefficients=',[(x['feature'],round(x['OR'],3),[round(t,3)for t in x['ORCI']])for x in z.get('coefficients',[])])

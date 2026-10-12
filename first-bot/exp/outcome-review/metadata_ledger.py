#!/usr/bin/env python3
"""Lightweight outcome-only census. Independently contrasts index with game JSON.
Does not decode raw replays, fit models, or run heavy computations. No overwrite.
"""
import collections,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[2];C=R/'.cache/outcome-review';E=R/'exp/outcome-review'
C.mkdir(parents=True,exist_ok=True)
waves=[('W0.1','cand-merge2-online'),('W0.2','cand-merge2-online-r2'),('W0.3','cand-merge2-online-r3')]
waves += [('W'+str(i),'cand-stack6-online-r2' if i==7 else 'cand-stack'+str(i if i<=6 else i-1)+'-online') for i in range(1,13)]
hist=['baseline-r1','baseline-r1b','baseline-r1c','cand-avoid6-online','cand-portal1-online','cand-swarm8-online','base-px8-online','base-px9d-online','px-king-v2-online']
rows=[];missing=[];seen=set();mismatch=[]
for w,s in waves+[(s,s) for s in hist]:
    d=R/'data/online'/s
    if not (d/'index.json').exists():missing.append({'wave':w,'set':s});continue
    idx=json.load(open(d/'index.json'))['games'];assert len(idx)==70
    for g in idx:
        assert g['gameId'] not in seen;seen.add(g['gameId'])
        assert g['opponentTeam'] in [306,70,20,801,264,46,545]
        j=json.load(open(d/('game-'+str(g['gameId'])+'.json')));q=j['replay']['result'];side=g['ourSide'].upper();en='B' if side=='A' else 'A'
        io='W' if (g['winner']or'').upper()==side else 'L' if (g['winner']or'').upper()==en else 'D'
        jo='W' if q['winner']==side else 'L' if q['winner']==en else 'D'
        if io!=jo:mismatch.append(g['gameId'])
        rows.append({'wave':w,'set':s,'id':g['gameId'],'era':'history' if s in hist else 'waves','opponent':g['opponentTeam'],'map':g['mapName'],'family':'r500' if g['mapName'] in ['Autarky','Portals','Schooltime','Slithery Fight','Trauma'] else 'elim','indexOutcome':io,'jsonOutcome':jo,'ourEliminated':q['team'+side]['dragonCount']==0,'theirEliminated':q['team'+en]['dragonCount']==0,'ourFinal':q['team'+side]['longestDragon'],'theirFinal':q['team'+en]['longestDragon']})
def wilson(k,n):
    if not n:return [None,None]
    z=1.95996398454;p=k/n;a=1+z*z/n;c=(p+z*z/(2*n))/a;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/a
    return [c-h,c+h]
def agg(a):
    n=len(a);i=collections.Counter(r['indexOutcome'] for r in a);j=collections.Counter(r['jsonOutcome'] for r in a)
    return {'N':n,'index':dict(i),'gameJSON':dict(j),'ourEliminated':sum(r['ourEliminated'] for r in a),'theirEliminated':sum(r['theirEliminated'] for r in a),'winCI':wilson(i['W'],n),'ourFinalSum':sum(r['ourFinal'] for r in a),'theirFinalSum':sum(r['theirFinal'] for r in a),'ourFinalMean':sum(r['ourFinal'] for r in a)/n if n else None,'theirFinalMean':sum(r['theirFinal'] for r in a)/n if n else None}
out={'N':len(rows),'missing':missing,'mismatchCount':len(mismatch),'mismatches':mismatch,'population':{},'cells':{}}
for era in ['waves','history']:
    for group in ['top6','DEV']:
        out['population'][era+'-'+group]=agg([r for r in rows if r['era']==era and (r['opponent']!=545)==(group=='top6')])
for w in dict.fromkeys(r['wave'] for r in rows):
    rr=[r for r in rows if r['wave']==w]
    cells={}
    for group in ['top6','DEV']:
        q=[r for r in rr if (r['opponent']!=545)==(group=='top6')]
        cells[group]=agg(q)
        for f in ['r500','elim']:cells[group+'-family-'+f]=agg([r for r in q if r['family']==f])
        for m in sorted(set(r['map'] for r in q)):cells[group+'-map-'+m]=agg([r for r in q if r['map']==m])
    for o in sorted(set(r['opponent'] for r in rr)):cells['opponent-'+str(o)]=agg([r for r in rr if r['opponent']==o])
    out['cells'][w]=cells
with open(C/'metadata-ledger.json','x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
lines=['# Outcome-only metadata census (provisional)','', 'Independent index and game-JSON counts; raw replay and model work is pending the resource exception.','', '| Wave | Group | N | Index W/D/L | JSON W/D/L | Our eliminated | Enemy eliminated | Final longest means own/enemy |','| --- | --- | --- | --- | --- | --- | --- | --- |']
for w,a in out['cells'].items():
    for g in ['top6','DEV']:
        z=a[g];fmt=lambda d:'/'.join(str(d.get(o,0)) for o in ['W','D','L'])
        lines.append(f"| {w} | {g} | {z['N']} | {fmt(z['index'])} | {fmt(z['gameJSON'])} | {z['ourEliminated']} | {z['theirEliminated']} | {z['ourFinalMean']:.2f}/{z['theirFinalMean']:.2f} |")
with open(E/'metadata-ledger.md','x') as f:f.write('\n'.join(lines)+'\n')
print(json.dumps({'N':out['N'],'population':out['population'],'mismatches':mismatch,'missing':missing},ensure_ascii=False))

#!/usr/bin/env python3
"""Lightweight exact arithmetic on the verified outcome-only census."""
import json,math,statistics as S
from pathlib import Path
R=Path(__file__).resolve().parents[2];C=R/'.cache/outcome-review'
first=json.load(open(C/'metadata-ledger.json'));audit=json.load(open(C/'metadata-audit.json'))
assert not audit['mismatchCount'] and first['N']==audit['N']
rep={'merge2':['W0.1','W0.2','W0.3'],'stack6':['W6','W7']}
chi=0;df=0
for b,names in list(rep.items()):
    a=[audit['waves'][w]['top6']['W'] for w in names];p=sum(a)/(60*len(a));v=60*p*(1-p)
    chi+=sum((x-S.mean(a))**2/v for x in a);df+=len(a)-1
    rep[b]={'N':len(a)*60,'wins':a,'winsTotal':sum(a),'winCountSD':S.stdev(a)}
phi=chi/df;ci=[chi/9.3484036045,chi/.2157952826];z=first['population']['waves-top6'];p0=z['index']['W']/z['N']
tab=[]
for plus in [3,5,10]:
    delta=plus/60;p1=p0+delta;pm=(p0+p1)/2
    for power,zbeta in [(.8,.84162123357),(.9,1.28155156554)]:
        n0=(1.95996398454*math.sqrt(2*pm*(1-pm))+zbeta*math.sqrt(p0*(1-p0)+p1*(1-p1)))**2/delta**2
        for label,inflation in [('binomial-floor',1),('measured-with-floor',max(1,phi)),('dispersion-upper95',max(1,ci[1]))]:
            n=math.ceil(n0*inflation);tab.append({'plusWinsPer60':plus,'power':power,'noise':label,'gamesPerArm':n,'totalGames':n*2,'wavesPerArm':math.ceil(n/60),'totalWaves':2*math.ceil(n/60)})
out={'replicates':rep,'residualDF':df,'dispersion':phi,'dispersionCI':ci,'p0':p0,'alpha':.05,'assumptions':'independent equal-size control/new arms, two-sided normal two-proportion approximation','table':tab}
with open(C/'metadata-power.json','x')as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'dispersion':phi,'dispersionCI':ci,'power80':[x for x in tab if x['power']==.8 and x['noise']=='measured-with-floor']}))
